import os
import subprocess
from string import Formatter


def write_qchem_input(path: str, template: str, keywords: dict, print_template=False):
    """TODO: Docstring for write_qchem_input.

    :path: TODO
    :template: TODO
    :keywords: TODO
    :returns: TODO

    """
    dirpath = os.path.split(path)[0]
    os.makedirs(dirpath, exist_ok=True)
    with open(path, 'w') as qin:
        for key, value in keywords.items():
            if value is None:
                print(f"** Warning: {key} is None **")
        
        inputstring = template.format(**keywords)
        
        if print_template:
            print(inputstring)
        qin.write(inputstring)


def send_qchem_to_cluster(path: str, method, **kwargs):
    """TODO: Docstring for send_qchem_to_cluster.

    :path: TODO
    :method: TODO
    :returns: TODO

    """
    formatfields = [fname for _, fname, _, _ in Formatter().parse(method) if fname]
    for key in kwargs.keys():
        if key not in formatfields:
            print(f'** Warning: send to cluster key {key} not availale in config "command"! Ignoring it!')
            kwargs.pop(key)
    cmdstring = method.format(path=path, **kwargs)
    subprocess.run(cmdstring, shell=True)
