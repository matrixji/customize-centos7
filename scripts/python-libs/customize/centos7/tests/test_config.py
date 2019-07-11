# pylint: disable=redefined-outer-name, protected-access

from collections import namedtuple
from os import (getpid, path, mkdir)
from shutil import rmtree
import pytest

from customize.centos7.config import Config


Project = namedtuple('Project', 'yaml, root')

@pytest.fixture(scope='function')
def project(request) -> Project:
    pid = getpid()
    project_dir = '/tmp/ut_temp_{}'.format(pid)
    mkdir(project_dir)
    def teardown_function():
        rmtree(project_dir, ignore_errors=True)
    request.addfinalizer(teardown_function)
    yield Project(root=project_dir, yaml=path.join(project_dir, 'main.yaml'))

def test_load_from_project(project):
    with open(project.yaml, 'w') as fp:
        fp.write('''
---
foo: 1
bar: 2
tom: ['a', b, c]
        ''')
    cfg = Config(project.root, [])
    assert cfg.get('foo') == 1

def test_load_from_non_project(project):
    with pytest.raises(FileNotFoundError):
        Config(project.root, [])


@pytest.mark.parametrize('args, key, val', (
    (['--foo', '1'], 'foo', 1),
    (['--foo', '1'], 'bar', None),
    (['--foo=1'], 'foo', 1),
    (['--foo.bar=1'], 'foo.bar', 1),
    (['--foo.bar=[1,2,3]', '--foo.bar.0=100'], 'foo.bar.0', 100),
))
def test_load_from_args(args, key, val):
    cfg = Config('-', args)
    assert cfg.get(key) == val

@pytest.mark.parametrize('args', (
    ['foo', '1'],
    ['-foo', '1'],
    ['-foo=1'],
))
def test_load_from_invalid_args(args):
    with pytest.raises(KeyError):
        Config('-', args)


@pytest.mark.parametrize('args, output', (
    (['--foo', '1'], ['--foo', '1']),
    (['--foo=1'], ['--foo', '1']),
    (['--foo=1', 'x'], ['--foo', '1', 'x']),
    (['--foo=a=b', 'x'], ['--foo', 'a=b', 'x']),
))
def test_format_args(args, output):
    assert Config._format_args(args) == output

@pytest.mark.parametrize('args, fmt, pattern', (
    (['--foo', '1'], 'yaml', 'foo: 1'),
    (['--foo', '1'], 'json', '"foo": 1'),
))
def test_dump(args, fmt, pattern):
    cfg = Config('', args)
    txt = cfg.dump(fmt)
    assert txt.find(pattern) >= 0
