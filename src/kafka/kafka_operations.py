import json


def load_conf(conf_file):
    with open(conf_file) as file:
        conf_val = json.load(file)
        return conf_val
