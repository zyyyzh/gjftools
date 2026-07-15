import os
from gjftools.gjftools import gjfdata


def get_xyzfile_length(xyzfile: str) -> int:
    '''
    get the number of structures in an xyz file
    '''
    with open(xyzfile, 'r') as xf:
        text = [x.strip() for x in xf.readlines() if x.strip() != '']
        # will delete all the blank lines in file
    atom_num = int(text[0])
    structure_len = atom_num + 2
    length = int(len(text) / structure_len)
    return length


def output_SI_coord(log_dir: str) -> str:
    '''
    get all coords from a directory of log files and output to
    one xyz file for paste to the SI part of papers.
    '''
    log_list = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    log_list.sort()

    total_xyz_list = []
    for log in log_list:
        log_file = os.path.join(os.path.abspath(log_dir), log)
        # read log
        _xyz = gjfdata()
        _xyz.get_body_from_log(log_file)
        # rename xyz title as log file name
        _xyz.title = log.split('.')[0]
        # crude str list
        _crude_list = _xyz.write_xyz(to_str_list=True)
        # do some modification
        _crude_list[0] = '\n'  # remove atom number
        _crude_list.insert(2, f'{_xyz.c_m}\n')  # add charge and multiplicity
        # combine str list
        total_xyz_list.extend(_crude_list)
    
    SI_coord_file = os.path.join(os.path.abspath(log_dir), 'SI_coord.xyz')
    with open(SI_coord_file, 'w') as coord:
        coord.writelines(total_xyz_list)
