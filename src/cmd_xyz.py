import sys
import configparser
import argparse

from molparser import mol_parser


def cmdparser():
    """TODO: Docstring for cmdparser.
    :returns: TODO

    """
    parser = argparse.ArgumentParser(description='A script for extracting xyz coordinates of qchem files')
    parser.add_argument('QOUT', nargs='+', help='the qchem output files')
    parser.add_argument('-i', '--input', action='store_true', help='wether to extract the initial or last geometry of an optimization/ts/ci calculation')

    return parser


def main(argv: list):
    """TODO: Docstring for main.
    :returns: TODO

    """
    config = configparser.ConfigParser()
    parser = cmdparser()
    args = vars(parser.parse_args(argv))

    for file in args['QOUT']:
        mol = mol_parser(file, config, read_rem=False, input_xyz=args['input'])['mol']

        print(file)
        print(mol)
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
