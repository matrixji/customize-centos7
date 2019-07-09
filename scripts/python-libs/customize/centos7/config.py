# encoding: utf-8

from os import path
from os import strerror
from errno import ENOENT
from typing import List, Any
import json
import yaml


class Config:

    _defaults = (
        ('name', 'mycent', 'Your distribution name'),
        ('verion', '0.1.0', 'Your distribution version number'),
    )

    def __init__(self, project_dir: str, args: Any = None) -> None:
        self.cfg = dict()
        self._load_project(project_dir)
        if args:
            self._apply_configs(args)

    def _load_default_cfg(self):
        for key, value, _ in Config._defaults:
            self._apply_config('--%s' % key, value)

    def _load_project(self, project_dir: str) -> None:
        self._load_default_cfg()
        if project_dir not in ('-', ''):
            config_path = path.join(project_dir, 'main.yaml')
            if not path.isfile(config_path):
                raise FileNotFoundError(ENOENT, strerror(ENOENT), config_path)
            with open(config_path) as fp:
                cfg = yaml.load(fp, yaml.loader.FullLoader)
                self.cfg.update(cfg)

    @staticmethod
    def _format_args(args: List[str]) -> List[str]:
        ret = list()
        for arg in args:
            index = arg.find('=')
            if arg.startswith('--') and index > 0:
                ret.append(arg[:index])
                ret.append(arg[index+1:])
            else:
                ret.append(arg)
        return ret

    def _apply_configs(self, args: List[str]) -> None:
        args = Config._format_args(args)
        if (len(args)) % 2 != 0:
            raise KeyError(args)
        for key, value in zip(args[::2], args[1::2]):
            if not key.startswith('--'):
                raise KeyError(key)
            key = key[2:]
            self._apply_config(key, value)

    def _apply_config(self, key: str, value: str) -> None:
        words = key.split('.')
        cfg = self.cfg
        for word in words[:-1]:
            if word.isdigit():
                cfg = cfg[int(word)]
            else:
                cfg[word] = cfg.get(word, dict())
                cfg = cfg[word]
        decoded_value = value
        try:
            decoded_value = json.loads(value)
        except ValueError:
            pass

        word = words[-1]
        if word.isdigit():
            cfg[int(word)] = decoded_value
        else:
            cfg[word] = decoded_value

    def get(self, key: str):
        keys = key.split('.')
        cfg = self.cfg
        for word in keys:
            if word.isdigit():
                try:
                    cfg = cfg[int(word)]
                except IndexError:
                    return None
            else:
                try:
                    cfg = cfg[word]
                except KeyError:
                    return None
        return cfg

    def dump(self, fmt='yaml'):
        if fmt == 'yaml':
            return yaml.dump(self.cfg)
        if fmt == 'json':
            return json.dumps(self.cfg)
        return self.cfg

    @staticmethod
    def get_default_configs():
        return Config._defaults
