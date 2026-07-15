'''
A class storing gjf file data.
Able to read from different source, modification and output new gjf file.

Author: Ye Zihao
Dated: 2024-01-16
'''
import os
from typing import Optional, List


num_to_ele = {'1': 'H', '2': 'He', '3': 'Li', '4': 'Be', '5': 'B', '6': 'C', '7': 'N', '8': 'O', '9': 'F', '10': 'Ne', '11': 'Na', '12': 'Mg', '13': 'Al', '14': 'Si', '15': 'P', '16': 'S', '17': 'Cl', '18': 'Ar', '19': 'K', '20': 'Ca', '21': 'Sc', '22': 'Ti', '23': 'V', '24': 'Cr', '25': 'Mn', '26': 'Fe', '27': 'Co', '28': 'Ni', '29': 'Cu', '30': 'Zn', '31': 'Ga', '32': 'Ge', '33': 'As', '34': 'Se', '35': 'Br', '36': 'Kr', '37': 'Rb', '38': 'Sr', '39': 'Y', '40': 'Zr', '41': 'Nb', '42': 'Mo', '43': 'Tc', '44': 'Ru', '45': 'Rh', '46': 'Pd', '47': 'Ag', '48': 'Cd', '49': 'In', '50': 'Sn', '51': 'Sb', '52': 'Te', '53': 'I', '54': 'Xe', '55': 'Cs', '56': 'Ba', '57': 'La', '58': 'Ce', '59': 'Pr', '60': 'Nd', '61': 'Pm', '62': 'Sm', '63': 'Eu', '64': 'Gd', '65': 'Tb', '66': 'Dy', '67': 'Ho', '68': 'Er', '69': 'Tm', '70': 'Yb', '71': 'Lu', '72': 'Hf', '73': 'Ta', '74': 'W', '75': 'Re', '76': 'Os', '77': 'Ir', '78': 'Pt', '79': 'Au', '80': 'Hg', '81': 'Tl', '82': 'Pb', '83': 'Bi', '84': 'Po', '85': 'At', '86': 'Rn', '87': 'Fr', '88': 'Ra', '89': 'Ac', '90': 'Th', '91': 'Pa', '92': 'U', '93': 'Np', '94': 'Pu', '95': 'Am', '96': 'Cm', '97': 'Bk', '98': 'Cf', '99': 'Es', '100': 'Fm', '101': 'Md', '102': 'No', '103': 'Lr', '104': 'Rf', '105': 'Db', '106': 'Sg', '107': 'Bh', '108': 'Hs', '109': 'Mt', '110': 'Ds', '111': 'Rg', '112': 'Cn', '113': 'Nh', '114': 'Fl', '115': 'Mc', '116': 'Lv', '117': 'Ts', '118': 'Og'}
DEFAULT_HEAD = ['%nprocshared=4\n',
                '%mem=8GB\n',
                '%chk=product-cf-SS-00001.chk\n',
                '#p opt freq=vcd nosymm b3lyp/6-31G*\n',
                '\n',
                'product-cf-SS-00001\n'
                '\n']


class gjfdata():
    '''A class storing gjf file data.
    Able to read from different source, modification and output new gjf file.
    '''
    def __init__(self,
                 nproc: int = 4,
                 mem: str = '4GB',
                 chk_name: str = None,
                 input_para: str = '#p opt freq b3lyp/6-31G*',
                 title: str = None,
                 c_m: str = '',
                 atom_element: List[str] = ['H'],
                 atom_type: List[int] = [0],
                 atom_info: List[str] = ['(Iso=2)'],
                 atom_coord: List[List[float]] = [[-1.081631,-0.429970,0.720089]],
                 tail: List[str] = [''],
                 output_name: str = None,
                 verbose: bool = False,
                 ):
        
        self.nproc = str(nproc)
        self.mem = mem
        self.chk_name = chk_name
        self.input_para = input_para
        self.title = title
        self.c_m = c_m
        self.atom_element = atom_element
        self.atom_type = atom_type
        self.atom_info = atom_info
        self.atom_coord = atom_coord
        self.tail = tail
        self.output_name = output_name
        self.verbose = verbose
        
        self.atom_num = len(atom_element)
        self.input_name = ''  # input file name, modified by different functions later.
        self.model_name = ''  # model file name, used only when no output name is given.

    def __len__(self):
        'return number of atoms in gjfdata'
        return self.atom_num

    def get_body_from_log(self,
                          logfile: str,
                          structure_index: int = -1):
        '''
        read coords from the last structure in logfile.
        '''
        self.input_name = logfile

        with open(self.input_name) as logf:
            loglines = logf.readlines()

        for i, line in enumerate(loglines):
            if line.strip().startswith('Symbolic Z-matrix:'):
                cm_line = loglines[i+1]
                self.c_m = f'{cm_line.split()[2]} {cm_line.split()[-1]}'
                break

        structure_index_list = []
        for i in range(len(loglines)):
            if 'NAtoms= ' in loglines[i]:
                atom_num = int(loglines[i].split()[1])
            if 'Input orientation:' in loglines[i] or 'Standard orientation:' in loglines[i]:
                structure_index_list.append(i)
        # read certain structure according to structure index given
        structure_line_index = structure_index_list[structure_index]

        coord_list = loglines[structure_line_index+5 : structure_line_index+5+atom_num]
        atom_element_list = []
        atom_type_list = []
        atom_coord_list = []
        for m in range(atom_num):
            atom_element, atom_type, coord_x, coord_y, coord_z = coord_list[m].split()[1:]
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_type_list.append(int(atom_type))
            atom_coord_list.append([coord_x, coord_y, coord_z])
        
        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = atom_type_list
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num

        if self.verbose:
            print(f'read structure info from {logfile} structure {structure_index}')
            print(f'{len(structure_index_list)} structures in {logfile}.')

    def get_body_from_xyz(self,
                          xyzfile: str,
                          structure_index: int = 0):
        '''
        read coords from certain structures in normal xyz file.
        '''
        self.input_name = xyzfile

        with open(xyzfile) as xf:
            xflines = xf.readlines()

        atom_num = int(xflines[0].strip())
        structure_len = atom_num + 2
        all_structure_list = [xflines[d:d+structure_len]
                              for d in range(0, len(xflines), structure_len)]

        coord_list = all_structure_list[structure_index]
        atom_element_list = []
        atom_coord_list = []
        for line in coord_list[2:]:
            atom_element, coord_x, coord_y, coord_z = line.split()
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_coord_list.append([coord_x, coord_y, coord_z])

        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = [0] * self.atom_num
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num
        
        if self.verbose:
            print(f'read structure info from {xyzfile} structure {structure_index}.')
            print(f'{len(all_structure_list)} structures in {xyzfile}.')

    def get_body_from_rpipmin(self,
                              xyzfile: str,
                              structure_index: int = 0,
                              tstmpe_index: int = None):
        '''
        read coords from certain structures in xyz file output by rpipmin.
        '''
        self.input_name = xyzfile

        with open(xyzfile) as xf:
            xflines = xf.readlines()

        atom_num = int(xflines[2].strip())
        structure_len = atom_num + 4
        all_structure_list = [xflines[d:d+structure_len]
                              for d in range(0, len(xflines), structure_len)][:-1]
        all_tstmpe_list = [int(structure[3].split()[1])
                           for structure in all_structure_list]
        
        if tstmpe_index is not None:
            coord_list = all_structure_list[all_tstmpe_list.index(tstmpe_index)]
        else:
            coord_list = all_structure_list[structure_index]

        atom_element_list = []
        atom_coord_list = []
        for line in coord_list[4:]:
            atom_element, coord_x, coord_y, coord_z = line.split()
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_coord_list.append([coord_x, coord_y, coord_z])

        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = [0] * self.atom_num
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num
        
        if self.verbose:
            print(f'read structure info from {xyzfile} tstmpe {tstmpe_index}.')
            print(f'{len(all_structure_list)} structures in {xyzfile}.')

    def get_body_from_irc(self,
                          ircfile: str,
                          irc_index: int):
        '''
        read coords from structures in irc log file and reorganize order
        for easier use.
        '''
        self.input_name = ircfile

        with open(self.input_name) as logf:
            loglines = logf.readlines()

        structure_index_list = []
        for i in range(len(loglines)):
            if 'NAtoms= ' in loglines[i]:
                atom_num = int(loglines[i].split()[1])
            if 'Input orientation:' in loglines[i] or 'Standard orientation:' in loglines[i]:
                structure_index_list.append(i)
        # read certain structure according to structure index given
        structure_line_index = structure_index_list[:-1]
        ircpoints = int(len(structure_index_list))

        reorg_index_list = [structure_line_index[-i] for i in range(1, (ircpoints+1)//2)]\
             + structure_line_index[:(ircpoints-1)//2+1]
   
        reorg_index = reorg_index_list[irc_index]
        coord_list = loglines[reorg_index+5 : reorg_index+5+atom_num]
        atom_element_list = []
        atom_type_list = []
        atom_coord_list = []
        for m in range(atom_num):
            atom_element, atom_type, coord_x, coord_y, coord_z = coord_list[m].split()[1:]
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_type_list.append(int(atom_type))
            atom_coord_list.append([coord_x, coord_y, coord_z])
        
        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = atom_type_list
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num

        if self.verbose:
            print(f'read structure info from {ircfile} irc_index {irc_index}')
            print(f'{ircpoints} structures in {ircfile}.')

    def get_body_from_gjf(self,
                          gjffile: str,
                          include_c_m: bool = True):
        '''
        read coords from gjf file.
        '''
        with open(gjffile) as gf:
            gflines = gf.readlines()

        emptyindex = []
        for i in range(len(gflines)):
            if gflines[i].strip() == '':
                emptyindex.append(i)

        coord_list = gflines[emptyindex[1]+2:emptyindex[2]]
        atom_num = len(coord_list)
        atom_element_list = []
        atom_type_list = []
        atom_coord_list = []
        for m in range(atom_num):
            split_line = coord_list[m].split()
            atom_element = split_line[0]
            coord_x, coord_y, coord_z = split_line[-3:]
            atom_type = split_line[1] if len(split_line) == 5 else '0'
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_type_list.append(int(atom_type))
            atom_coord_list.append([coord_x, coord_y, coord_z])
        
        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = atom_type_list
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num

        c_m = gflines[emptyindex[1]+1].strip()
        if include_c_m:  # include charge and multiplicity
            self.c_m = c_m
        
        if self.verbose:
            print(f'read structure info from {gjffile}')

    def get_body_from_sdf(self,
                          sdffile: str,
                          structure_index: int = 0,
                          read_title: bool = False):
        '''
        read coords from certain structures in normal xyz file.
        '''
        self.input_name = sdffile

        with open(sdffile) as sf:
            sflines = sf.readlines()

        info_line_list = []
        end_line_list = []
        for i, line in enumerate(sflines):
            if len(line.split()) == 11 and line.split()[-2] == '0999':
                info_line_list.append(i)
            elif "M  END" in line:
                end_line_list.append(i)

        all_structure_list = []
        for i , info_index in enumerate(info_line_list):
            end_index = end_line_list[i]
            if end_index == len(sflines) - 1:
                all_structure_list.append(sflines[info_index-3:])
            else:
                all_structure_list.append(sflines[info_index-3:end_index])

        coord_list = all_structure_list[structure_index]
        atom_num = int(coord_list[3].split()[0])
        if read_title:
            self.title = coord_list[1].strip()
        atom_element_list = []
        atom_coord_list = []
        for line in coord_list[4:atom_num+4]:
            coord_x, coord_y, coord_z, atom_element = line.split()[:4]
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_coord_list.append([coord_x, coord_y, coord_z])

        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = [0] * self.atom_num
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num
        
        if self.verbose:
            print(f'read structure info from {sdffile} structure {structure_index}.')
            print(f'{len(all_structure_list)} structures in {sdffile}.')

    def get_body_from_xtbscan(self,
                              modfile: str,
                              highest_energy: bool = False,
                              structure_index: int = -1,
                              ):
        '''read coords from gau-xtb scan modredundant log file.
        '''
        self.input_name = modfile

        with open(modfile) as modf:
            modlines = modf.readlines()

        structure_index_list = []  # 144
        scan_point_list = []  # 143
        energy_list = []

        for i, line in enumerate(modlines):
            if 'NAtoms= ' in modlines[i]:
                atom_num = int(modlines[i].split()[1])
            elif 'Input orientation:' in line or 'Standard orientation:' in line:
                structure_index_list.append(i)
            elif 'scan point' in line:
                scan_point_list.append({'step': int(line.split()[2]),
                                        'scan': int(line.split()[-4]),
                                        'total': int(line.split()[-1])})
            elif line.strip().startswith('Energy='):
                energy_list.append(float(line.split()[1]))

        true_structure_index_list = []
        true_energy_list = []
        for j, info in enumerate(scan_point_list):
            if info['step'] == 1 and info['scan'] != 1:
                true_energy_list.append(energy_list[j-1])
                true_structure_index_list.append(structure_index_list[j-1])
        true_energy_list.append(energy_list[len(scan_point_list)-1])
        true_structure_index_list.append(structure_index_list[len(scan_point_list)-1])

        if highest_energy:  # get highest energy TS like structure
            tmp_energy = -9999.9
            for index, energy in enumerate(true_energy_list):
                if index == 0 or index == len(true_energy_list)-1:
                    continue
                elif energy > true_energy_list[index-1] and energy > true_energy_list[index+1]:
                    tmp_energy = max(tmp_energy, energy)
            if tmp_energy == -9999.9:
                raise RuntimeError('no TS like structure! please check manually.')
            else:
                structure_index = true_energy_list.index(tmp_energy)

        structure_line_index = true_structure_index_list[structure_index]

        coord_list = modlines[structure_line_index + 5:
                              structure_line_index + 5 + atom_num]
        atom_element_list = []
        atom_type_list = []
        atom_coord_list = []
        for m in range(atom_num):
            atom_element, atom_type, coord_x, coord_y, coord_z = coord_list[m].split()[1:]
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_type_list.append(int(atom_type))
            atom_coord_list.append([coord_x, coord_y, coord_z])
        
        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = atom_type_list
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num

        if self.verbose:
            print(f'read structure info from {modfile} scan point {structure_index}')
            print(f'{len(true_structure_index_list)} structures in {modfile}.')

    def get_body_from_gauscan(self,
                              modfile: str,
                              highest_energy: bool = False,
                              structure_index: int = -1,
                              ):
        '''read coords from gau-xtb scan modredundant log file.
        '''
        self.input_name = modfile

        with open(modfile) as modf:
            modlines = modf.readlines()

        structure_index_list = []  # 144
        scan_point_list = []  # 143
        energy_list = []

        for i, line in enumerate(modlines):
            if 'NAtoms= ' in modlines[i]:
                atom_num = int(modlines[i].split()[1])
            elif 'Input orientation:' in line or 'Standard orientation:' in line:
                structure_index_list.append(i)
            elif 'scan point' in line:
                scan_point_list.append({'step': int(line.split()[2]),
                                        'scan': int(line.split()[-4]),
                                        'total': int(line.split()[-1])})
            elif line.strip().startswith('SCF Done'):
                energy_list.append(float(line.split()[4]))

        true_structure_index_list = []
        true_energy_list = []
        for j, info in enumerate(scan_point_list):
            if info['step'] == 1 and info['scan'] != 1:
                true_energy_list.append(energy_list[j-1])
                true_structure_index_list.append(structure_index_list[j-1])
        true_energy_list.append(energy_list[len(scan_point_list)-1])
        true_structure_index_list.append(structure_index_list[len(scan_point_list)-1])

        if highest_energy:  # get highest energy TS like structure
            tmp_energy = -9999.9
            for index, energy in enumerate(true_energy_list):
                if index == 0 or index == len(true_energy_list)-1:
                    continue
                elif energy > true_energy_list[index-1] and energy > true_energy_list[index+1]:
                    tmp_energy = max(tmp_energy, energy)
            if tmp_energy == -9999.9:
                raise RuntimeError('no TS like structure! please check manually.')
            else:
                structure_index = true_energy_list.index(tmp_energy)

        structure_line_index = true_structure_index_list[structure_index]

        coord_list = modlines[structure_line_index + 5:
                              structure_line_index + 5 + atom_num]
        atom_element_list = []
        atom_type_list = []
        atom_coord_list = []
        for m in range(atom_num):
            atom_element, atom_type, coord_x, coord_y, coord_z = coord_list[m].split()[1:]
            if atom_element.isdigit():
                atom_element = num_to_ele[atom_element]
            atom_element_list.append(atom_element)
            atom_type_list.append(int(atom_type))
            atom_coord_list.append([coord_x, coord_y, coord_z])
        
        self.atom_num = atom_num
        self.atom_element = atom_element_list
        self.atom_type = atom_type_list
        self.atom_coord = atom_coord_list
        self.atom_info = [''] * self.atom_num

        if self.verbose:
            print(f'read structure info from {modfile} scan point {structure_index}')
            print(f'{len(true_structure_index_list)} structures in {modfile}.')

    def get_model_file(self,
                       modelfile: str):
        '''
        read head and tail from model gjf file.
        '''
        self.model_name = modelfile

        with open(modelfile) as mf:
            mflines = mf.readlines()

        emptyindex = []
        for i in range(len(mflines)):
            if mflines[i].strip() == '':
                emptyindex.append(i)
        
        setup_lines = mflines[:emptyindex[0]]
        for i, line in enumerate(setup_lines):
            if line.strip().startswith('%nproc'):
                self.nproc = line.strip().split('=')[-1]
            if line.strip().startswith('%mem'):
                self.mem = line.strip().split('=')[-1]
            # if line.strip().startswith('%chk'):
            #     self.chk_name = line.strip().split('=')[-1]
            if line.strip().startswith('#'):
                self.input_para = ''
                for inpline in setup_lines[i:]:
                    self.input_para += f'{inpline.strip()} '

        # if mflines[emptyindex[0]+1].strip() != 'Title Card Required':
        #     self.title = mflines[emptyindex[0]+1].strip()

        if self.c_m == '':
            self.c_m = mflines[emptyindex[1]+1].strip()

        mftail = mflines[emptyindex[2]:]
        self.tail = mftail

        if self.verbose:
            print(f'read head and tail from {modelfile}.')

    def write_gjf(self,
                  output_name: str = None,
                  need_chk: bool = True,
                  check_basis: bool = True,
                  ) -> Optional[str]:
        '''
        combine all components and write to a gjf.
        optionally output info to terminal for check.
        '''
        if output_name == None:
            self.output_name = f'''{os.path.dirname(self.input_name)}/{os.path.basename(self.input_name).split('.')[0]}_{os.path.basename(self.model_name).split('.')[0]}'''
        elif os.path.dirname(output_name) == '':
            self.output_name = os.path.join(
                os.path.dirname(self.input_name),
                os.path.basename(output_name).split('.')[0],
                )
        else:
            self.output_name = output_name.split('.')[0]

        if self.chk_name == None:
            self.chk_name = os.path.basename(self.output_name)
        else:
            self.chk_name = self.chk_name.split('.')[0]

        if self.title == None:
            self.title = os.path.basename(self.output_name)

        headlines = []
        headlines.append(f'%nprocshared={self.nproc}\n')
        headlines.append(f'%mem={self.mem}\n')
        if need_chk:
            headlines.append(f'%chk={self.chk_name}.chk\n')
        headlines.append(f'{self.input_para}\n')
        headlines.append('\n')
        headlines.append(f'{self.title}\n')
        headlines.append('\n')
        headlines.append(f'{self.c_m}\n')

        if check_basis:
            self._compair_basis_element()

        headlines = self._replace_placeholder(headlines)

        body_list = []
        for a in range(self.atom_num):
            atom_line = f'''{self.atom_element[a]}{self.atom_info[a]}    \
                {self.atom_type[a]}    {'  '.join(self.atom_coord[a])}\n'''
            body_list.append(atom_line)
        
        out_gjf_list = headlines + body_list + self.tail
        with open(self.output_name+'.gjf', 'w') as gjf:
            gjf.writelines(out_gjf_list)
        
        if self.verbose:
            print(f'''write gjf file to {self.output_name+'.gjf'}.''')

    def write_xyz(self,
                  output_name: str=None):
        '''
        combine all components and write to a xyz.
        '''
        if output_name == None:
            self.output_name = f'''{os.path.dirname(self.input_name)}/{os.path.basename(self.input_name).split('.')[0]}_{os.path.basename(self.model_name).split('.')[0]}'''
        elif os.path.dirname(output_name) == '':
            self.output_name = os.path.join(
                os.path.dirname(self.input_name),
                os.path.basename(output_name).split('.')[0],
                )
        else:
            self.output_name = output_name.split('.')[0]

        if self.title == None:
            self.title = os.path.basename(self.output_name)

        body_list = []
        for a in range(self.atom_num):
            atom_line = f'''{self.atom_element[a]}    {'  '.join(self.atom_coord[a])}\n'''
            body_list.append(atom_line)
        
        out_xyz_list = [str(len(self.atom_element)) + '\n',
                        self.title + '\n'] + body_list
        with open(self.output_name+'.xyz', 'w') as xyz:
            xyz.writelines(out_xyz_list)
        
        if self.verbose:
            print(f'''write xyz file to {self.output_name+'.xyz'}.''')

    def _compair_basis_element(self):
        basis_element_lineid = []
        element_dict = {}
        for j in range(len(self.tail)):  # modify basis info accordingly
            if '****' in self.tail[j]:
                if self.tail[j-2].split()[-1] == '0':
                    for ele in self.tail[j-2].split()[:-1]:
                        element_dict[ele] = j-2  # get elements in model basis setting
                    basis_element_lineid.append(j-2)
        
        if len(basis_element_lineid) > 0:  # basis part exist
            element_set = set(element_dict.keys())
            atom_element_set = set(self.atom_element)  # get elements in structure, output set
            basis_element_list = self.tail[basis_element_lineid[0]].split()[:-1]
            if len(element_set.difference(atom_element_set)) > 0:
                for e in element_set.difference(atom_element_set):
                    basis_element_list.remove(e)  # more elements in basis than coord, to be removed
            elif len(atom_element_set.difference(element_set)) > 0:
                for e in atom_element_set.difference(element_set):
                    basis_element_list.append(e)  # more elements in coord than in basis, to be added
            else:
                pass
            basis_element_list.append('0')
            basis_element_line = ' '.join(basis_element_list) + '\n'
            self.tail[basis_element_lineid[0]] = basis_element_line

    def _replace_placeholder(self,
                             headlines: str):
        placeholder = r'''{replace}'''

        replacer = os.path.basename(self.output_name)

        for i, headline in enumerate(headlines):
            if placeholder in headline:
                headlines[i] = headline.replace(placeholder, replacer)
        
        for j, tailline in enumerate(self.tail):
            if placeholder in tailline:
                self.tail[j] = tailline.replace(placeholder, replacer)

        return headlines
