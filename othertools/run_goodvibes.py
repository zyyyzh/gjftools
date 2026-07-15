'''run goodvibes on gaussian output file and collect result
Author: Zihao Ye
creation time: 2023-09-20

Goodvibes installation: conda install -c patonlab goodvibes
tqdm installation: conda install tqdm
'''

import os
import argparse
from tqdm import tqdm


def run_gv(file_name: str,
           temp: float):
    output_name = file_name.split('.')[0]
    gvcmd = f'python -m goodvibes {file_name} -q -t {temp} --output {output_name} > /dev/null'
    os.system(gvcmd)
    return f'Goodvibes_{output_name}.dat'


def read_gv(dat_name: str,
            is_remove: bool):
    with open(dat_name, 'r') as dat:
        dat_lines = dat.readlines()
    
    csv_line = ''
    for line in dat_lines:
        if line.startswith('o'):
            csv_line = ','.join(line.split()[1:]) + '\n'

    if is_remove:
        os.remove(dat_name)
        
    return csv_line


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--dir', '-d',
        default='.',
        help='workdir path (default: current dir)',
    )
    p.add_argument(
        '--temp', '-t',
        default=298.15,
        help='temperature for calculating free energy (default: 298.15 K)',
    )
    p.add_argument(
        '--clean', '-c',
        action='store_const',
        const=True,
        default=False,
        help='remove finished dat files (default: False)',
    )
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    abs_dir = os.path.abspath(args.dir)
    os.chdir(abs_dir)

    # run goodvibes
    dat_file_list = []
    for file in tqdm(os.listdir(abs_dir), desc='running goodvibes'):
        if file.endswith('.log'):
            dat_file_list.append(run_gv(file, temp=args.temp))
    dat_file_list.sort()

    # read output
    csv_lines = ['name,E,ZPE,H,qh-H,T.S,T.qh-S,G(T),qh-G(T)\n']
    for file in tqdm(dat_file_list, desc='reading output'):
        csv_line = read_gv(file, is_remove=args.clean)
        if csv_line != '':
            csv_lines.append(csv_line)
    
    with open('gvibes_result.csv', 'w') as f:
        f.writelines(csv_lines)
