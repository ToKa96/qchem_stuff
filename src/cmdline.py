#!/export/home/tkaczun/anaconda3/bin/python
import os
import argparse
import re

from configparser import ConfigParser

from configloader import load_config
from templateparser import load_templates
from molparser import mol_parser
from writeinput import write_qchem_input, send_qchem_to_cluster


def cmdparser():
    """TODO: Docstring for cmdparser.
    :returns: TODO

    """
    # - Option to extract most rem data and reuse it from existing file?
    # TODO: hwo to deal with different keywords in different templates?
    parser = argparse.ArgumentParser(description='A script for automating the creation of qchem input files.')
    parser.add_argument('TEMPLATE',
                        help='the base name of the qchem template or path to it')
    # TODO: how to get the coordinates?
    parser.add_argument('MOLFILE', nargs='+', help='A file from which the xyz coordinates of the molecule can be read.')
    parser.add_argument('-o', '--output', action='append', help='the names to be used for the output')
    parser.add_argument('-p', '--print', action='store_true', help='prints all availale keywords in the given template and their defaults')
    parser.add_argument('--input_xyz', action='store_true', help='read the input mol xyz structur if it is an optimization rather than the last one')
    parser.add_argument('--read_rem', help='will use the methods, basis, etc from the given MOLFILE', action='store_true')
    parser.add_argument('--send', action='store_true', help='if given send the input file to the cluster')

    # qchem related keywords
    parser.add_argument('-m', '--method', help='the method value')
    parser.add_argument('-b', '--basis', help='the method value')
    parser.add_argument('-c', '--charge', default=0, type=int, help='Charge of the molecule')
    parser.add_argument('--mult', type=int, default=1, help='Multiplicity of the molecule (2S+1)')
    parser.add_argument('--dft_d', help='specifies dft d correction type')
    parser.add_argument('-k', '--keywords', help='specify further keywords by key value pairs as strings', action='extend')

    # qsys related keywords
    parser.add_argument('-t', '--walltime', help='the walltime for the cluster')
    parser.add_argument('-n', '--ncpus', help='the number of threads to be used', type=int)
    # TODO: write converter for ram to mb for qchem
    parser.add_argument('-r', '--ram', help='amount of memory to be used in mb')

    return parser


def cmd_main(argv: list):
    """TODO: Docstring for cmd_main.

    :argv: TODO
    :returns: TODO

    """
    config = load_config()
    parser = cmdparser()
    args = vars(parser.parse_args(argv))

    args = args_mod(args, config)

    templatedata = load_templates(args['TEMPLATE'])

    if args['print']:
        print_template(templatedata)

    for molfile, outfile in zip(args['MOLFILE'], args['output']):
        moldata = mol_parser(molfile, config, read_rem=args['read_rem'], input_xyz=args['input_xyz'])
        keywords = dict()
        for key, value in templatedata['defaults'].items():
            keywords[key] = value
            try:
                keywords[key] = moldata[key]
            except KeyError:
                print(f'using default for {key}')
        keywords = update_keywords_with_args(keywords, args)
        write_qchem_input(outfile, templatedata['template'], keywords, print_template=args['print'])

        if args['send']:
            send_qchem_to_cluster(outfile, config['job send']['command'])


def update_keywords_with_args(keywords: dict, args: dict):
    for key in keywords.keys():
        try:
            if args[key] is not None:
                keywords[key] = args[key]
        except KeyError:
            pass

    for argkey, key in zip(['ram', 'ncpus'], ['mem_total', 'threads']):
        if args[argkey] is not None:
            keywords[key] = args[argkey]

    return keywords


def args_mod(args: dict, config: ConfigParser):
    templatepath = config['templates']['template_dir']
    template_base = args['TEMPLATE']
    template = ''
    if not os.path.isfile(template):
        if not template_base.endswith('.template'):
            template = template_base + '.template'

    args['TEMPLATE'] = os.path.join(templatepath, template)

    if args['output'] is None:
        args['output'] = []
        for molfile in args['MOLFILE']:
            args['output'].append(molfile + f'.{template_base}.in')
    elif len(args['output']) == len(args['MOLFILE']):
        pass
    else:
        print(args['output'])
        print(args['MOLFILE'])
        raise ValueError('Not enough filenames supplied to -o, --output')

    if args['ram'] is not None:
        args['ram'] = mem_parser(args['ram'])

    return args


def print_template(templatedata: dict):
    print('** Qchem Template **')
    print()
    print('keywords and default values:')

    for key, value in templatedata['defaults'].items():
        print(f'  {key:15} = {value}')

    print()
    print('** template **')
    print()
    print(templatedata['template'])
    print()
    print('** end **')


def mem_parser(ram: str):
    """TODO: Docstring for mem_parser.
    :returns: TODO

    """
    ram_return = 0
    matches = re.findall(r'(\d+)(\D+)', ram)

    if len(matches) > 1:
        print(f'unusual string for mem keyword encountered: {ram}')
    if matches:
        ram_return = int(matches[0][0])
        if 'gb' in matches[0][1].lower():
            ram_return *= 1000
    else:
        try:
            ram_return = int(ram)
        except ValueError:
            raise ValueError(f'Invalid ram encountered could not be converted to integer ({ram})')

    return ram_return


if __name__ == "__main__":
    import sys
    cmd_main(sys.argv[1:])
