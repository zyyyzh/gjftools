# collect and process sobEDA and sobEDAw output file
# Author: Zihao Ye
# creation time: Oct, 2023

import os
import re
import csv
import argparse
from typing import List


def get_sob_EDA_result(log_file) -> List:
    '''read sobEDA results
    Return (kcal/mol) list of:
        total interaction energy
        electrostatic
        exchange
        pauli repulsion
        exchange-repulsion
        oribital
        DFT correlation
        dispersion correction
        coulomb correlation
    '''
    with open(log_file, 'r') as log:
        log_lines = log.readlines()
    
    result_list = []
    for i, line in enumerate(log_lines):
        if line.startswith('Total interaction energy:'):
            tot_index = i
            result_list.append(line.split()[-2])
            energy_list = [log_lines[i+x].split()[-2] for x in range(3,11)]
            result_list += energy_list
            break
    
    if result_list:
        return result_list
    else:
        return ['0.0'] * 9


def get_sob_EDA_weak_result(log_file) -> List:
    '''read sobEDAw results
    Return (kcal/mol) list of:
        electrostatic
        exchange-repulsion
        oribital
        dispersion correction
    '''
    with open(log_file, 'r') as log:
        log_lines = log.readlines()
    
    result_list = []
    for i, line in enumerate(log_lines):
        if line.startswith('Variant of sobEDA for weak interaction'):
            tot_index = i
            energy_list = [log_lines[i+x].split()[-2] for x in range(2,6)]
            result_list += energy_list
            break
    
    if result_list:
        return result_list
    else:
        return ['0.0'] * 4


def main(dir: str=os.getcwd()):
    '''
    process all log file in dir and its sub dir startswith numbers
    determine whether they are normal termination
    if normal termination,
        get different interaction energies
    output to a csv file
    '''
    # make log dir, collect log file and get log_path
    os.chdir(dir)
    os.system('rm -rf log')
    os.makedirs('log', exist_ok=True)
    for dir in os.listdir():
        if dir.endswith('.log'):
            os.system(f'cp {dir} log/')
    for dir in os.listdir():
        if dir.isdigit():
            os.system(f'cp {dir}/*.log log/')
    log_path = os.path.abspath('log')

    # process log file
    log_list = [file for file in os.listdir(log_path)
                if file.endswith('.log') or file.endswith('.out')]
    log_list.sort()

    out_dict = {}
    for file in log_list:
        log_file = os.path.abspath(log_path + '/' + file)
        out_dict[file] = (get_sob_EDA_result(log_file) +
                          get_sob_EDA_weak_result(log_file))
    
    # write to csv
    with open(log_path + '/sobedaprocess.csv', mode='w', newline="") as w:
        w.write(f'file_name,tot_int_energy,elec_energy,ex_energy,pauli_energy,'
                f'ex_pauli,orib_energy,DFTc_energy,disp_energy,coul_energy,'
                f'w_elec_energy,w_ex_pauli,w_orib_energy,w_disp_energy\n')

        for file in log_list:
            out_line = ','.join(out_dict[file])
            w.write(f'{file},{out_line}\n')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--dir', '-d',
        default='.',
        help='workdir path (default: current dir)',
    )
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    abs_dir = os.path.abspath(args.dir)
    main(abs_dir)
