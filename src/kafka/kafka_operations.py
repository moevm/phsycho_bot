import json


def load_conf(conf_file):
    with open(conf_file) as f:
        conf_val = json.load(f)
        return conf_val
