import os

import yaml

from dmdoc.utils.envvars import resolve_any


def is_yaml_file(filepath: str):
    return os.path.isfile(filepath) and (
        filepath.endswith('.yaml') or filepath.endswith('.yml')
    )


def read_yaml(filepath: str):
    with open(filepath, mode="r") as f:
        return yaml.safe_load(f)


def read_yaml_with_envvars(filepath: str):
    content = read_yaml(filepath)
    return resolve_any(content)
