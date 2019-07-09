# encoding: utf-8

class ConfigurationError(Exception):
    def __init__(self, mess):
        Exception.__init__(self, mess)
