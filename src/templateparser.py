import os
from string import Formatter


def load_templates(fns):
    if isinstance(fns, list):
        for i, fn in enumerate(fns):
            try:
                return load_template(os.path.expanduser(fn))
            except FileNotFoundError:
                if i == len(fns) - 1:
                    raise FileNotFoundError('No template file found!')
    elif isinstance(fns, str):
        return load_template(os.path.expanduser(fns))
    else:
        raise TypeError(f'No valid type supplied {fns}')


def load_template(fn: str):
    """TODO: Docstring for load_template.

    :fn: TODO
    :returns: TODO

    """
    comments: str = ''
    template: str = ''

    with open(fn) as file:
        for line in file:
            if line.startswith('#'):
                comments += line
            else:
                template += line

    formatfields = [fname for _, fname, _, _ in Formatter().parse(template) if fname]
    defaults = read_defaults(comments, formatfields)

    return {'template': template, 'defaults': defaults}


def read_defaults(comments: str, formatfields: list):
    """TODO: Docstring for read_defaults.

    :comments: TODO
    :returns: TODO

    """
    formatnames = [fname.lower() for fname in formatfields]

    ret = dict()

    comments = comments.replace('#', ' ')
    comments = comments.replace('\n', ' ')
    split = iter(comments.split())
    for word in split:
        if word.lower() in formatnames:

            i = formatnames.index(word.lower())
            formatnames.pop(i)
            key = formatfields.pop(i)
            value = next(split)
            ret[key] = value

    for key in formatfields:
        ret[key] = ''

    return ret


if __name__ == "__main__":
    fn = 'test/data/template_test.in'

    ret = load_template(fn)
    print(ret)
