import json

import importlib.resources as pkg_resources

from avalon.exception import AvalonError

from . import resources


def get_rules():

    filename = "rules.json"

    try:
        with pkg_resources.path(resources, filename) as rules_path:
            with open(rules_path, "r") as infile:
                rules = json.load(infile)
    except FileNotFoundError:
        raise AvalonError("File '{}' doesn't exist!".format(filename))
    except json.decoder.JSONDecodeError:
        raise AvalonError("File '{}' can't be decoded!".format(filename))

    return rules

if __name__ == '__main__':
    print(get_rules())
