import os
import argparse
from typing import List

def get_isotropic_value(nmr_file: str, element: str=None):
    
    with open(nmr_file) as f:
        nmr_list = [line for line in f.readlines() 
                    if len(line.split()) >= 6]

    result_line = ''

    for nmr_line in nmr_list:
        split_line = nmr_line.split()
        if split_line[2] == 'Isotropic':
            if element:
                if split_line[1] == element:
                    result_line += f'{split_line[0]},' \
                                   f'{split_line[1]},' \
                                   f'{split_line[4]},'
            else:
                result_line += f'{split_line[0]},' \
                               f'{split_line[1]},' \
                               f'{split_line[4]},'
    result_line += '\n'
    return result_line

def main(log_path: str, element: str=None):
    # process log file
    gau_list = [file for file in os.listdir(log_path)
                if file.endswith('.log') or file.endswith('.out')]
    gau_list.sort()

    out_list = []
    for file in gau_list:
        gau_file = os.path.abspath(log_path + '/' + file)
        nmr_result_line = get_isotropic_value(gau_file, element)
        out_list.append(f'{file},{nmr_result_line}')

    # write to csv
    with open(log_path + '/get_nmr.csv', mode='w') as w:
        w.write('file_name,nmr_results\n')
        for result in out_list:
            w.writelines(result)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--dir', '-d',
        default='.',
        help='workdir path (default: current dir)',
    )
    p.add_argument(
        '--element', '-e',
        default='H',
        help='element to get (default: H)',
    )
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()

    main(log_path=args.dir, element=args.element)
