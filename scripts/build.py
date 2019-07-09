#!/usr/bin/env python3

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
    pass


def build():
    if len(sys.argv) < 3:
        usage()
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
