import os
import re
import argparse

JOB_DICT = {
    'g09': {'script': '/usr/bin/g09yzh01',
            'filetype': 'gjf'},
    'g16': {'script': '/usr/bin/g16yzh01',
            'filetype': 'gjf'},
    'crest': {'script': '/home/yzh/gjftools/othertools/qg09/yzhcrest01',
              'filetype': 'xyz'},
    'crestopt': {'script': '/home/yzh/gjftools/othertools/qg09/yzhcrestopt01',
              'filetype': 'xyz'},
    'crest2opt': {'script': '/home/yzh/gjftools/othertools/qg09/yzhcrest2opt01',
              'filetype': 'xyz'},
    'xtb': {'script': '/usr/bin/g09xtb01',
            'filetype': 'gjf'},
    'rpip': {'script': '/usr/bin/yzhcf801',
             'filetype': 'gjf'},
    'g09fix': {'script': '/usr/bin/g09yzh01fix',
               'filetype': 'gjf'},
}

class Job():
    def __init__(
        self,
        processor: int,
        jobtype: str,
        qhost: str,
        **kwargs,
        ):
        self.processor = processor
        self.script = JOB_DICT[jobtype]['script']
        self.filetype = JOB_DICT[jobtype]['filetype']
        self.qhost = f''' -q all.q@{qhost}''' if qhost else ''
        self.extra_var = ''

        print('='*25, 'pyqsub', '='*25)
        print(f'Job type: {jobtype}')
        print(f'Number of processors: {self.processor}')

        if kwargs:
            for key, value in kwargs.items():
                self.extra_var += f',{key.upper()}={value}'
            print(f'Extra variables: {self.extra_var[1:]}')
        print()

    def __call__(
        self,
        filename: str,  # full abs path
        ):
        jobname = os.path.basename(filename).split('.')[0]
        dirname = os.path.dirname(filename)
        var = f''' -v JOBNAME={jobname},DIR_NAME={dirname}{self.extra_var}'''

        print(f'Input file directory: {dirname}')
        print(f'Job name: {jobname}')
        qsub_cmd = f'''qsub{var}{self.qhost} -cwd -j y -S /bin/bash -pe smp {self.processor} -N {jobname} {self.script}'''

        os.system(qsub_cmd)
        print()


def main(
    job,  # jobclass object
    filename,
    is_all,
    ):
    if filename:
        if is_all:
            print(('''Warning! Provide input file and ask to submit all files at the same time! Ignore submitting all files!'''))
        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)

        job(filename)
    elif is_all:
        cwd = os.getcwd()
        sublist = []
        for f in os.listdir(cwd):
            if f.endswith(f'.{job.filetype}'):
                prefix = f.split('.')[0]
                prefix = prefix.replace('+', '\+')
                pofile_regex = prefix+'\.po\d+'
                is_pofile = False
                ofile_regex = prefix+'\.o\d+'
                is_ofile = False
                for ff in os.listdir():
                    ofile_match = re.match(ofile_regex, ff)
                    if ofile_match != None:
                        is_ofile = True
                        break
                    pofile_match = re.match(pofile_regex, ff)
                    if pofile_match != None:
                        is_pofile = True
                        break
                if not is_pofile and not is_ofile:
                    sublist.append(os.path.abspath(f))

        sublist = list(set(sublist))
        sublist.sort()
        for sub in sublist:
            job(sub)

        print(f'Submit {len(sublist)} jobs in total!')
    else:
        raise RuntimeError(f'No input file given!')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--processor', '-p',
        type=int,
        default=4,
        help='Number of processors (default=4).'
    )
    p.add_argument(
        '--jobtype', '-j',
        type=str,
        default='g09',
        help=f'Type of job (default=g09), type avaliable: {JOB_DICT}'
    )
    p.add_argument(
        '--file', '-f',
        type=str,
        default=None,
        help='File to be submitted.'
    )
    p.add_argument(
        '--all', '-a',
        action='store_const',
        const=True,
        default=False,
        help='Submit all files under current folder.',
    )
    p.add_argument(
        '--qhost', '-q',
        type=str,
        default=None,
        help='Designate host to be submitted to (or not to with ! before hostname).'
    )
    p.add_argument(
        '--charge', '-c',
        type=int,
        default=0,
        help='Charge of the system (default=0, only avaliable with some job types).'
    )
    p.add_argument(
        '--spin', '-s',
        type=int,
        default=1,
        help='Spin of the system (default=1, only avaliable with some job types).'
    )

    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()

    extra_dict = {}
    if args.charge != 0 or args.spin != 1:
        extra_dict = {'charge': args.charge, 'spin': args.spin}

    jobclass = Job(
        args.processor,
        args.jobtype,
        args.qhost,
        **extra_dict,
    )

    main(
        job=jobclass,
        filename=args.file,
        is_all=args.all,
    )
