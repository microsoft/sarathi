import argparse
import datetime
import os
from typing import Any

import yaml

from vllm.benchmark.constants import DEFAULT_CONFIG_FILE


def custom_bool(val):
    if val.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif val.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class Config:

    def __init__(self, args: dict):
        self._args = args

    def __getattr__(self, name):
        return self._args.get(name, None)

    def __reduce__(self):
        return self.__class__, (self._args, )


class ConfigParser:

    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        self._parser = argparse.ArgumentParser()
        self._args = None
        self._load_yaml(config_file)
        self._parse_args()
        self._add_derived_args()
        self._write_yaml_to_file()

    def _load_yaml(self, filename):
        with open(filename, "r") as file:
            yaml_config = yaml.safe_load(file)
        self._update_namespace(yaml_config)

    def _parse_args(self):
        self._args = self._parser.parse_args()

    def _add_derived_args(self):
        print(self._args)
        self._args.output_dir = f"{self._args.output_dir}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        os.makedirs(self._args.output_dir, exist_ok=True)

    def _update_namespace(self, config_dict, parent_key=""):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                new_key = f"{parent_key}{key}_" if parent_key else f"{key}_"
                self._update_namespace(value, new_key)
            else:
                arg_name = f"{parent_key}{key}"

                if type(value) == bool:
                    self._parser.add_argument(
                        f"--{arg_name}",
                        type=custom_bool,
                        nargs='?',
                        const=True,
                        default=value,
                    )
                else:
                    self._parser.add_argument(f"--{arg_name}",
                                              default=value,
                                              type=type(value))

    def get_config(self):
        return Config(self._args.__dict__)

    def get_yaml(self):
        return yaml.dump(self._args.__dict__, default_flow_style=False)

    def _write_yaml_to_file(self):
        with open(f"{self._args.output_dir}/benchmark_config.yml",
                  "w") as file:
            file.write(self.get_yaml())

    def to_dict(self):
        return self._args.__dict__
