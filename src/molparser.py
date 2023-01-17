import subprocess
from configparser import ConfigParser


def mol_parser(path: str, config: ConfigParser, read_rem=False, input_xyz=False):
    """TODO: Docstring for mol_parser.

    :path: TODO
    :config: TODO
    :returns: TODO

    """
    if path.endswith('.xyz'):
        return read_xyz(path, config)
    elif path.endswith('.out'):
        return read_qchem(path, config, read_rem, input_xyz)
    else:
        raise NotImplementedError('Mol parser currently only implemented for .xyz and qchem files')


def read_xyz(path: str, config: ConfigParser):
    """TODO: Docstring for read_xyz.

    :path: TODO
    :config: TODO
    :returns: TODO

    """
    mol = ''
    try:
        mol = subprocess.run(config['mol']['xyz'].format(path=path))
    except KeyError:
        with open(path) as xyz:
            for i, line in enumerate(xyz):
                if i == 0:
                    pass
                elif i == 1:
                    try:
                        split = line.split()
                        for i in range(1, 4):
                            float(split[i])
                    except ValueError:
                        pass
                    else:
                        mol += line
                else:
                    mol += line
    return {'mol': mol}


def read_qchem(path: str, config: ConfigParser, read_rem: bool, input_xyz: bool):
    """TODO: Docstring for read_qchem.

    :path: TODO
    :config: TODO
    :read_rem: TODO
    :input_xyz: TODO
    :returns: TODO

    """
    ret = None
    geojobs = ['opt', 'ts']
    geo = False
    if input_xyz:
        ret = read_qchem_others(path, config)
    else:
        with open(path) as qout:
            for line in qout:
                if "jobtype" in line.lower():
                    if line.lower().split()[-1] in geojobs:
                        geo = True
                    break

    if geo:
        ret = read_qchem_opt(path, config)
    else:
        if ret is None:
            ret = read_qchem_others(path, config)

    if read_rem:
        rem_dict = parse_rem(path)
        ret.update(**rem_dict)

    return ret


def read_qchem_opt(path: str, config: ConfigParser):
    """TODO: Docstring for read_qchem_opt.

    :path: TODO
    :config: TODO
    :read_rem: TODO
    :input_xyz: TODO
    :returns: TODO

    """
    try:
        mol = subprocess.run(config['mol']['qchem_geo'].format(path=path))
    except KeyError:
        raise NotImplementedError('No standard parser for qchem geo yet implemented')

    return {'mol': mol}


def read_qchem_others(path: str, config: ConfigParser):
    """TODO: Docstring for read_qchem_others.

    :path: TODO
    :config: TODO
    :read_rem: TODO
    :returns: TODO

    """
    try:
        mol = subprocess.run(config['mol']['qchem_input'].format(path=path))
    except KeyError:
        raise NotImplementedError('No standard parser for qchem inputs yet implemented')

    return {'mol': mol}


def parse_rem(path):
    ret = dict()
    rem = False
    with open(path) as qout:
        for line in qout:
            if "$end" in line:
                rem = False
            if rem:
                split = line.split()
                key = split[0].lower()
                value = split[1]
                ret[key] = value
            if "$rem" in line:
                rem = True
    return ret
