#!/usr/bin/env python3

import logging
import logging.handlers
import sys
from customize.centos7.builder import Builder

def usage():
    # called by build-tool
    cmd = './build-tool'
    print('usage: %s action [options]' % cmd)
    print('  for show help : %s help' % cmd)
    print('  for build image: %s build <project-directory> [options]' % cmd)
    print('  for show build options: %s list-options' % cmd)
    exit(1)


def list_options():
    print('Not ready')


def init_log():
    log = logging.getLogger('mycent')
    log.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    log.addHandler(stream_handler)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    stream_handler.setFormatter(formatter)


def build():
    if len(sys.argv) < 3:
        usage()

    init_log()
    project_dir = sys.argv[2]
    builder = Builder(project_dir, sys.argv[3:])
    builder.build()


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('build', 'list-options'):
        usage()
    action = sys.argv[1]
    if action == 'list-options':
        list_options()
    elif action == 'build':
        build()
