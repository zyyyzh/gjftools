# collect and process gaussian output file
# Author: Zihao Ye
# creation time: Dec, 2022
# version: 2026/07/15

import os
import re
import sys
import csv
import time
import argparse
from copy import copy
from typing import List

# 
PATTERN_LIST = [
    r'CCSD\(T\)=(-?\d+\.\d+)(\\|\|)R',
    r'MP2=(-?\d+\.\d+)(\\|\|)R',
    r'HF=(-?\d+\.\d+)(\\|\|)R'
]

# bash command to get queue info
QUEUE_CMD = "qstat -u zye"


def get_termination(gauf):
    '''
    judge whether the job has terminated normally
    '''
    is_normal = 0 
    try:
        for i in range(1,10):
            if 'Normal termination' in gauf[-i]:
                is_normal = 1
                break
    except:
        is_normal = 0

    return is_normal


def get_imag_freq(gauf):
    '''
    get number of imaginary freqencies if avaliable.
    if no freq info, return -1
    '''
    try:
        num_imag = 0
        num_real = 0
        freq_cons = 0.0
        for line in gauf:
            if line.strip().startswith('Frequencies --'):
                freqs = line.split()[2:]
                for fr in freqs:
                    if float(fr) < 0.0:
                        num_imag += 1
                        if float(fr) < freq_cons:
                            freq_cons = float(fr)
                    elif float(fr) > 0.0:
                        num_real += 1
                        if freq_cons == 0.0:
                            freq_cons = float(fr)
                if num_real:
                    break
    except:
        num_imag = -1
        freq_cons = 0.0
    
    if num_imag == 0 and num_real == 0:
        num_imag = -1
        freq_cons = 0.0
    
    return num_imag, freq_cons


def get_sp_energy(gauf: List[str]) -> float:
    gauf = [x.strip() for x in gauf]
    gauf = ''.join(gauf)
    gauf = gauf.replace('\n', '')
    for pattern in PATTERN_LIST:
        match = re.search(pattern, gauf)
        if match:
            try:
                spenergy = float(match.group(1))
                break
            except ValueError:
                spenergy = -1.0
        else:
            spenergy = -1.0
    return spenergy


def get_free_energy(gauf):
    '''
    get free energy data in gaussian output file
    if error occurs, return -1.0
    '''
    free_correction = 0.0
    free_energy = 0.0
    try:
        for i in range(len(gauf)):
            if 'Thermal correction to Gibbs Free Energy=' in gauf[i]:
                free_correction = gauf[i].split()[-1]
            if 'Sum of electronic and thermal Free Energies=' in gauf[i]:
                free_energy = gauf[i].split()[-1]

        free_correction = float(free_correction)
        free_energy = float(free_energy)
    except:
        free_correction = -1.0
        free_energy = -1.0

    return free_correction, free_energy


def get_optimization_points(gauf):
    '''
    get how many optimization points are there in the output file
    by searching for Step number * in the file
    '''
    rev_gauf = copy(gauf)
    rev_gauf.reverse() # search from the bottom

    optimation_points = 0
    try:
        for i in range(len(rev_gauf)):
            
            if 'Step number' in rev_gauf[i]:
                optimation_points = rev_gauf[i].split()[2]
                break
        optimation_points = int(optimation_points)
    except:
        optimation_points = -1
    
    return optimation_points


def get_converge_status(gauf):
    '''
    get converge status for optimization jobs
    number refers to how many 'yes' are there in the last step
    '''
    rev_gauf = copy(gauf)
    rev_gauf.reverse() # search from the bottom

    converge_status = 0
    try:
        for i in range(len(rev_gauf)):
            if 'Converged?' in rev_gauf[i]:
                for j in range(1,5):
                    if rev_gauf[i-j].split()[-1] == 'YES':
                        converge_status += 1
                break
    except:
        converge_status = -1

    return converge_status


def get_entropy(gauf):
    '''
    get different (rot, trans, vib, total) entropies from freq calculation
    useful when doing correction for implicit solvent model
    '''
    tot_S = -1.0
    elec_S = -1.0
    trans_S = -1.0
    rot_S = -1.0
    vib_S = -1.0

    for i in range(len(gauf)):
        if 'Sum of electronic and thermal Free Energies=' in gauf[i]:
            idx = i + 4
            tot_S = float(gauf[idx].split()[-1])
            elec_S = float(gauf[idx+1].split()[-1])
            trans_S = float(gauf[idx+2].split()[-1])
            rot_S = float(gauf[idx+3].split()[-1])
            vib_S = float(gauf[idx+4].split()[-1])
            break

    return tot_S, elec_S, trans_S, rot_S, vib_S


def _scan_for_files(main_dir: str, extension: str) -> bool:
    '''scan main_dir and its numbered subdirectories for files with given extension'''
    for f in os.listdir(main_dir):
        if f.endswith(extension):
            return True
    for d in os.listdir(main_dir):
        dirpath = os.path.join(main_dir, d)
        if d.isdigit() and os.path.isdir(dirpath):
            try:
                if any(f.endswith(extension) for f in os.listdir(dirpath)):
                    return True
            except PermissionError:
                pass
    return False


def main(main_dir: str=os.getcwd(),
         clean: bool=False,
         need_fchk: bool=None,
         need_file47: bool=None,
         need_time: bool=False,
         need_error: bool=False,
         deepclean: bool=False,
         all_yes: bool=False,
         ):
    '''
    process all log or out file in dir and its sub dir startswith numbers
    determine whether they are normal termination
    if normal termination,
        get single point energy (HF=)
        get gibbs free energy correction and free energy
    if running or error,
        get optimization points
        get converge status
    output to a csv file
    '''
    # check if deepclean is required
    if deepclean:
        if all_yes:
            pass
        else:
            need_deepclean = input('Do you want delete error files? (y/n)')
            if need_deepclean != 'y':
                print('Aborted! Exit now!')
                sys.exit()
            else:
                pass
    # make log dir, collect log file and get log_path
    os.chdir(main_dir)
    if os.path.exists('log'):
        if all_yes:
            os.system('rm -rf log')
        else:
            print('Warning: old log folder exists!')
            need_remove = input('Do you want delete old log? (y/n)')
            if need_remove == 'y':
                os.system('rm -rf log')
            else:
                os.system(f'mv log log_{int(time.time()*100)}')
    os.makedirs('log', exist_ok=True)

    # Auto-detect .fchk and .47 files if not explicitly set
    if need_fchk is None:
        need_fchk = _scan_for_files(main_dir, '.fchk')
    if need_file47 is None:
        need_file47 = _scan_for_files(main_dir, '.47')

    if need_fchk:
        if os.path.exists('fchk'):
            if all_yes:
                os.system('rm -rf fchk')
            else:
                print('Warning: old fchk folder exists!')
                need_remove = input('Do you want delete old fchk? (y/n)')
                if need_remove == 'y':
                    os.system('rm -rf fchk')
                else:
                    os.system(f'mv fchk fchk_{int(time.time()*100)}')
        os.makedirs('fchk', exist_ok=True)
    if need_file47:
        if os.path.exists('file47'):
            if all_yes:
                os.system('rm -rf file47')
            else:
                print('Warning: old file47 folder exists!')
                need_remove = input('Do you want delete old file47? (y/n)')
                if need_remove == 'y':
                    os.system('rm -rf file47')
                else:
                    os.system(f'mv file47 file47_{int(time.time()*100)}')
        os.makedirs('file47', exist_ok=True)
    if need_error:
        os.makedirs('log/error', exist_ok=True)

    timecp0 = time.time()
    for f in os.listdir():  # direct get files
        if f.endswith('.log'):
            os.system(f'cp {f} log/')
        elif f.endswith('.fchk'):
            if need_fchk:
                os.system(f'cp {f} fchk/')
        elif f.endswith('.47'):
            if need_file47:
                os.system(f'cp {f} file47/')
    
    for dir in os.listdir():  # get files from directories
        if dir.isdigit():
            os.system(f'cp {dir}/*.log log/')
            if need_fchk:
                os.system(f'cp {dir}/*.fchk fchk/')
            if need_file47:
                os.system(f'cp {dir}/*.47 file47/')

    log_path = os.path.abspath('log')
    timecp1 = time.time()
    if need_time:
        print(f'cp files time: {timecp1-timecp0}s')

    # read running jobs
    queue_log = os.path.abspath(log_path + '/queue.log')
    os.system(f'{QUEUE_CMD} > {queue_log}')
    with open(queue_log, 'r') as l:
        queue_lines = l.readlines()
    running_jobid = [line.split()[0] for line in queue_lines[1:]]
    os.system(f'rm -rf {queue_log}')

    # process log file
    gau_list = [file for file in os.listdir(log_path)
                if file.endswith('.log') or file.endswith('.out')]
    gau_list.sort()

    out_list = []
    remove_list = []
    for file in gau_list:
        gau_file = os.path.abspath(log_path + '/' + file)
        time0 = time.time()
        with open(gau_file) as f:
            gauf = f.readlines()
        time1 = time.time()
        if need_time:
            print(f'readfile {gau_file} time: {time1-time0}s')

        if get_termination(gauf):  # normal termination
            time2 = time.time()
            spenergy = get_sp_energy(gauf)
            time3 = time.time()
            free_correction, free_energy = get_free_energy(gauf)
            time4 = time.time()
            if (free_energy != 0.0) or (free_energy != -1.0):
                time5 = time.time()
                num_imag, freq_cons = get_imag_freq(gauf)
                tot_S, elec_S, trans_S, rot_S, vib_S = get_entropy(gauf)
                time6 = time.time()
            else:
                num_imag = -1
                freq_cons = 0.0
                tot_S, elec_S, trans_S, rot_S, vib_S = -1.0
            if need_time:
                print(f'getsp: {time3-time2}s')
                print(f'getfree: {time4-time3}s')
                print(f'getfreq: {time6-time5}s')

            out_list.append([file, 'Normol', '{:.7f}'.format(float(spenergy)),
             '{:.7f}'.format(float(free_correction)), '{:.7f}'.format(float(free_energy)),
             '{}'.format(num_imag), '{:.2f}'.format(freq_cons),
             '{:.3f}'.format(tot_S), '{:.3f}'.format(elec_S), '{:.3f}'.format(trans_S),
             '{:.3f}'.format(rot_S), '{:.3f}'.format(vib_S), ' ', ' '])

            # get jobid
            ofile_list = [of for of in os.listdir(main_dir) if of.startswith(f"{file.split('.')[0]}.o")]
            if not ofile_list:
                jobid = ''
            else:
                ofile = ofile_list[0]
                jobid = ofile.split('.o')[-1]

            remove_list.append((file, jobid))  # prepare for later cleanup

        else:  # abnormal termination or running
            time7 = time.time()
            opt_points = get_optimization_points(gauf)
            time8 = time.time()
            converge_status = get_converge_status(gauf)
            time9 = time.time()
            # get jobid
            ofile_list = [of for of in os.listdir(main_dir) if of.startswith(f"{file.split('.')[0]}.o")]
            if not ofile_list:
                jobid = ''
            else:
                ofile = ofile_list[0]
                jobid = ofile.split('.o')[-1]
            # determine running or error
            if jobid in running_jobid:  # running
                print(f'file {file} is still running!')
                out_list.append([file, 'Running', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', opt_points, converge_status]) 
            else:  # error
                print(f'file {file} did not terminate normally!')
                if need_error:
                    os.system(f'cp log/{file} log/error/')
                if deepclean:
                    remove_list.append((file, jobid))
                out_list.append([file, 'Error', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', opt_points, converge_status])    

            if need_time:
                print(f'getopt: {time8-time7}s')
                print(f'getconv: {time9-time8}s')

    # write to csv
    with open(log_path + '/gauprocess.csv', mode='w', newline="") as w:
        writer = csv.writer(w)
        writer.writerow(['file_name', 'status', 'sp_energy',
            'free_correction', 'free_energy',
            'num_imag_freq', 'freq_cons',
            'tot_S', 'elec_S', 'trans_S', 'rot_S', 'vib_S',
            'opt_points', 'converge_status'])
        writer.writerows(out_list)
    
    # clean up file and dirs
    if clean or deepclean:
        for log_file, jobid in remove_list:
            prefix = log_file.split('.')[0]
            print(f'{prefix} is now deleting...')
            os.system(f'rm -f {prefix}.log')
            os.system(f'rm -f {prefix}.gjf')
            os.system(f'rm -f {prefix}.o*')
            os.system(f'rm -f {prefix}.po*')
            os.system(f'rm -rf {jobid}')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--clean', '-c',
        action='store_const',
        const=True,
        default=False,
        help='remove finished job files (default: False)',
    )
    p.add_argument(
        '--deepclean', '-d',
        action='store_const',
        const=True,
        default=False,
        help='remove finished job files and error job files (default: False)',
    )
    p.add_argument(
        '--time', '-t',
        action='store_const',
        const=True,
        default=False,
        help='print out time for each step (default: False)',
    )
    p.add_argument(
        '--error', '-e',
        action='store_const',
        const=True,
        default=False,
        help='copy all error files to one single folder (default: False)',
    )
    p.add_argument(
        '--yes', '-y',
        action='store_const',
        const=True,
        default=False,
        help='input y for all confirmation (default: False)',
    )
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()

    main(clean=args.clean,
         need_time=args.time,
         need_error=args.error,
         deepclean=args.deepclean,
         all_yes=args.yes,
         )
