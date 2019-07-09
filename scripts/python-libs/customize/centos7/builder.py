# encoding: utf-8

from customize.centos7.config import Config

class Builder():
    def __init__(self, project_dir, args):
        self.cfg = Config(project_dir, args)

    def build(self):
        pass

    def hello(self):
        pass
