import os
import configparser


def load_config():
    """TODO: Docstring for load_global_config.
    :returns: TODO

    """
    configfiles = []

    home = os.path.expanduser('~')
    home += '/.config/qchem_scripts/config'
    configfiles.append(home)

    cwd = os.getcwd()

    for root, dirs, files in os.walk(cwd, topdown=False):
        for name in files:
            if name == '.qchem_scripts.conf':
                configfiles.append(os.path.join(root, name))

    config = configparser.ConfigParser()
    config.read(configfiles)

    if not config.sections():
        inp = input(f'Do you want to write a standard config file to {home}')
        if 'y' in inp.lower():
            write_standard_config(home)
            config.read(home)
        else:
            raise FileNotFoundError('No config file availale')

    return config


def write_standard_config(path: str):
    """TODO: Docstring for write_standard_config.
    :returns: TODO

    """
    templatesdir, _ = os.path.split(path)
    templatesdir += os.path.join(templatesdir, 'templates/')
    configstring = f"""
    # specifies where the template files lie
    [templates]
    templatesdirs = {templatesdir}
    # specify which script to call to send jobs to clusters (and create their
    # input files)
    [job send]
    command = 'qchem_send_job --send {{path}}'
    """
    os.makedirs(path, exist_ok=True)
    with open(path, 'r') as conf:
        conf.write(configstring)
