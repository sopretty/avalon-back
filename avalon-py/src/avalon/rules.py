from json import load


def load_rules():
    with open("resources/rules.json", "r") as infile:
        return load(infile)
