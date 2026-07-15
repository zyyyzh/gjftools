# collect and process gaussian output file
# Author: Zihao Ye
# creation time: Dec, 2022

import os
import re
import csv
import sys
import argparse
import logging


common_error_dict = {
    'l103': {
        'error_msg': [
            'Error in internal coordinate system',
            'Linear angle in Bend',
            'Linear angle in Tors',
            'FormBX had a problem',
        ],
        'fix': {'': set()},
    },
    'l123': {
        'error_msg': [
            'Maximum number of corrector steps exceded',
            'GS2 Optimization Failure.',
        ],
        'fix': {'irc': set(['lqa'])},
    },
    'l502': {
        'error_msg': [
            'Convergence failure -- run terminated.',
        ],
        'fix': {'scf': set(['novaracc', 'noincfock', 'vshift=500', 'conver=6', 'xqc'])},
    },
    'l9999': {
        'error_msg': [
            '-- Number of steps exceeded',
        ],
        'fix': {'opt': set(['calcfc', 'maxstep=5', 'notrustupdate'])},
    },
}

def parse_log_file(log_file):
    '''
    parse input line and final lines from the log file
    Arg:
        log_file: input log file
    Returns:
        final_lines: last 1000 lines of the log file
        input_lines: input line of the log file
    '''
    with open(log_file) as f:
        gauf = f.readlines()
    final_lines = [gauf[-i] for i in range(1, 1000)]

    start_lines = gauf[:200]
    for i, line in enumerate(start_lines):
        if (line.strip().startswith('-----') and
            start_lines[i+1].strip().startswith('#')):
            input_index = i+1
            break
    
    input_lines = ''
    for j in range(10):
        if start_lines[input_index+j].strip().startswith('-----'):
            break
        else:
            input_lines += start_lines[input_index+j].strip().lower()

    return final_lines, input_lines

def get_termination(final_lines):
    '''
    judge whether the job has terminated normally
    Arg:
        final_lines: last 1000 lines of the log file
    Return:
        status: status of the log file, can be Normal, Unknown, Error or error link number
    '''
    status = 'Unknown'  # maybe running or error

    for line in final_lines:
        if 'Normal termination' in line:
            status = 'Normal'
            return status
        if 'Error termination' in line:
            error_regex = 'l\d+\.exe'
            error_match = re.search(error_regex, line)
            if error_match != None:
                error_string = error_match.group(0)
                status = error_string.split('.')[0]
            else:
                status = 'Error'
            return status

    return status

def get_error_fix(error_number, final_lines):
    if error_number not in common_error_dict.keys():
        return 'No fix'
    
    error_msg = common_error_dict[error_number]['error_msg']

    for line in final_lines:
        for msg in error_msg:
            if msg in line:
                return common_error_dict[error_number]['fix']
    
    return 'No fix'

def fix_input(input_line, fix):
    fix_kw = list(fix.keys())[0]
    if not fix_kw:
        return input_line
    
    input_kw_list = input_line.split()

    for i, kw in enumerate(input_kw_list):
        if kw.startswith(fix_kw):
            fix_set = fix[fix_kw]
            if kw == fix_kw:
                kw_set = set()
            elif ',' not in kw:
                kw_set = set(kw.split('=')[-1])
            else:
                set_str = kw.split('(')[-1].split(')')[0]
                kw_set = set(set_str.split(','))
            new_kw_set = kw_set | fix_set

            if len(new_kw_set) == 0:
                new_kw = fix_kw
            elif len(new_kw_set) == 1:
                new_kw = f'''{fix_kw}={','.join(list(new_kw_set))}'''
            else:
                new_kw = f'''{fix_kw}=({','.join(list(new_kw_set))})'''
            input_kw_list[i] = new_kw
    
    fixed_input = (' ').join(input_kw_list)
    return fixed_input

def generate_new_gjf(log_file, gjf_file, fixed_input, fixed_gjf_file):
    from gjftools import gjfdata
    gjf = gjfdata()
    gjf.get_body_from_log(log_file)
    gjf.get_model_file(gjf_file)
    gjf.input_para = fixed_input
    gjf.write_gjf(fixed_gjf_file, check_basis=False)


def main(log_file, logger):
    log_file = os.path.abspath(log_file)
    log_dir = os.path.dirname(log_file)
    file_name = os.path.basename(log_file)
    
    final_lines, input_lines = parse_log_file(log_file)
    status = get_termination(final_lines)
    logger.info(f'{log_file} status: {status}')
    if status in ['Normal', 'Error', 'Unknown']:
        return None
    else:
        fix = get_error_fix(status, final_lines)
        logger.info(f'{log_file} fix: {fix}')
        if fix == 'No fix':
            return None
        else:
            fixed_input = fix_input(input_lines, fix)
            backup_log_file = log_file.replace('.log', '-backup.log')
            gjf_file = log_file.replace('.log', '.gjf')
            backup_gjf_file = gjf_file.replace('.gjf', '-backup.gjf')
            os.system(f'mv {log_file} {backup_log_file}')
            os.system(f'mv {gjf_file} {backup_gjf_file}')
            generate_new_gjf(backup_log_file, backup_gjf_file, fixed_input, gjf_file)
            logger.info('fixed gjf based on common error successful')
            with open('autofixok', 'w') as w:
                w.write('')
            return gjf_file


if __name__ == '__main__':
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('auto_fix.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    log_file = sys.argv[1]

    main(log_file, logger)
