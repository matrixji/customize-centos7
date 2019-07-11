# encoding: utf-8
# pylint: disable=broad-except,subprocess-popen-preexec-fn

from os import (setsid, killpg, getpgid)
from signal import SIGKILL
from subprocess import (Popen, PIPE)
import threading


class Action(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.error = None
        self.output = ''
        self.outerr = ''

    def run(self):
        raise NotImplementedError()

class ShellCommand(Action):
    def __init__(self, cmd: str, timeout=None):
        Action.__init__(self)
        self.cmd = cmd
        self.timeout = timeout
        self.fp = None

    def run(self):
        self.fp = Popen(self.cmd, shell=True, stdout=PIPE, stderr=PIPE, preexec_fn=setsid)
        output, outerr = self.fp.communicate(timeout=self.timeout)
        self.output = output.decode('utf-8')
        self.outerr = outerr.decode('utf-8')
        if self.fp.returncode != 0:
            self.error = 'Error: {}'.format(self.fp.returncode)

    def stop(self):
        if self.fp and self.is_alive():
            killpg(getpgid(self.fp.pid), SIGKILL)

    def __repr__(self):
        return u'<ShellCommand:%s>' % self.cmd

class PythonCode(Action):
    def __init__(self, func, *args):
        Action.__init__(self)
        self.func = func
        self.args = list(args)

    def run(self):
        try:
            self.func(*self.args)
        except Exception as error:
            self.error = error

    def stop(self):
        pass

    def __repr__(self):
        return u'<PythonCode:%s(%s)>' % (self.func, ','.join(self.args))
