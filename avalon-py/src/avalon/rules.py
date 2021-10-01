import json
import importlib.resources as pkg_resources

from . import resources


def get_rules():

    with pkg_resources.path(resources, "rules.json") as rules_path:
        with open(rules_path, "r") as infile:
            rules = json.load(infile)

    return rules
