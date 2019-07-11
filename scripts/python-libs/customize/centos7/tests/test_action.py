# pylint: disable=redefined-outer-name, protected-access

import pytest
from customize.centos7.action import ShellCommand, PythonCode

@pytest.mark.parametrize('cmd, err', (
    ('exit 1', 'Error: 1'),
    ('exit 0', None),
))
def test_shell_command(cmd, err):
    shell = ShellCommand(cmd)
    shell.run()
    assert shell.error == err

@pytest.mark.parametrize('code, has_error', (
    (lambda: 0/0, True),
    (lambda: 1, False),
))
def test_py_code(code, has_error):
    code = PythonCode(code)
    code.run()
    assert (code.error is not None) == has_error

def test_py_code_with_args():
    code = PythonCode(lambda x, y: 100/(x+y), 0, 0)
    code.run()
    assert code.error is not None

    code = PythonCode(lambda x, y: 100/(x+y), 0, 1)
    code.run()
    assert code.error is None
