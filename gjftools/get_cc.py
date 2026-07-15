import os
import argparse
from typing import List
from itertools import combinations

def get_crosscoupling_value(cc_file: str, atom_list: list):
    
    with open(cc_file) as f:
        cc_file_lines = f.readlines()
    
    possible_start = []
    for i, line in enumerate(cc_file_lines):
        if line.strip().startswith('NAtoms='):
            N_atoms = int(line.split()[1])
        if line.strip().endswith('J (Hz):'):
            possible_start.append(i)
    
    CC_start = possible_start[-1]

    for j, line in enumerate(cc_file_lines[CC_start+1:]):
        if not line.strip()[0].isdigit():
            CC_end = j + 1 + CC_start
            break
    
    CC_lines = cc_file_lines[CC_start:CC_end]
    print('length of cc lines', len(CC_lines))

    title_line_index = []
    for i, cc_line in enumerate(CC_lines):
        if cc_line.count('.') == 0 and i != 0:
            title_line_index.append(i)

    cc_dict = {}

    for index in title_line_index:
        title_line = CC_lines[index]
        for k, atom in enumerate(title_line.split()):
            atom = int(atom)
            atom_cc_dict = {}
            for a in range(atom+1, N_atoms+1):
                target_index = index + (k + 1) + (a - atom)
                cc_value = CC_lines[target_index].split()[k + 1]
                cc_float = float(cc_value.replace('D', 'E'))
                atom_cc_dict[a] = cc_float
            cc_dict[atom] = atom_cc_dict

    result_line = ''
    atom_pairs = combinations(atom_list, 2)
    for pair in atom_pairs:
        result_line += f'{pair},{cc_dict[pair[0]][pair[1]]}\n'

    return result_line

def main(log_path: str, atom_list: list):
    # process log file
    gau_list = [file for file in os.listdir(log_path)
                if file.endswith('.log') or file.endswith('.out')]
    gau_list.sort()

    for file in gau_list:
        gau_file = os.path.abspath(log_path + '/' + file)
        cc_result_line = get_crosscoupling_value(gau_file, atom_list)

        # write to csv
        with open(f'{log_path}/{file}_get_cc.csv', mode='w') as w:
            w.write('atom_pair,cc_results\n')
            w.writelines(cc_result_line)

# def parse_args():
#     p = argparse.ArgumentParser()
#     p.add_argument(
#         '--dir', '-d',
#         default='.',
#         help='workdir path (default: current dir)',
#     )
#     p.add_argument(
#         '--element', '-e',
#         default='H',
#         help='element to get (default: H)',
#     )
#     return p.parse_args()

if __name__ == '__main__':
    # args = parse_args()
    atom_list = [3,4,5,6,7,8,16]
    cc_dir = '/home/yzh/g09/test'
    main(log_path=cc_dir, atom_list=atom_list)
    # print(get_crosscoupling_value(cc_file, atom_list))
