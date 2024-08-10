from pytest import raises
from sympy import Symbol, Number, S
from warnings import catch_warnings
from nodimo._internal import (
    _is_running_on_jupyter, _show_object, _print_horizontal_line, _sympify_number,
    _unsympify_number, _prettify_name, NodimoWarning, _nodimo_formatwarning,
    _show_nodimo_warning
)


def test_environment():
    assert not _is_running_on_jupyter


def test_show_object(capfd):
    a = Symbol('alpha')
    _show_object(a)
    out_a, _ = capfd.readouterr()
    assert out_a == '\nα\n\n'


def test_horizontal_line(capfd):
    _print_horizontal_line()
    out, _ = capfd.readouterr()
    assert out == 78 * '-' + '\n'


def test_sympify_number():
    assert _sympify_number(5) == Number(5)
    assert _sympify_number(7/2) == Number(7,2)
    assert _sympify_number((7,2)) == Number(7,2)
    assert _sympify_number(3.5) == Number(7,2)
    assert _sympify_number(2.5551) == Number(2.5551)
    assert _sympify_number(Number(5.8)) == Number(5.8)
    assert _sympify_number('pi') == S.Pi
    assert _sympify_number('sqrt(3)') == Number(3)**Number(1,2)
    
    with raises(ValueError):
        _sympify_number('x')


def test_unsympify_number():
    assert _unsympify_number(Number(5)) == 5
    assert _unsympify_number(Number(7,2)) == (7,2)
    assert _unsympify_number(Number(2.5551)) == 2.5551
    assert _unsympify_number(S.Pi) == 'pi'
    assert _unsympify_number(Number(3)**Number(1,2)) == 'sqrt(3)'

    with raises(ValueError):
        _unsympify_number(Symbol('x'))


def test_prettify_name():
    assert _prettify_name('a') == 'a'
    assert _prettify_name('a', bold=True) == '𝐚'
    assert _prettify_name('1/3') == '1/3'

    with raises(ValueError):
        _prettify_name('1', bold=True)


def test_nodimo_formatwarning():
    message = _nodimo_formatwarning('nodimo warning message', NodimoWarning, None, None)
    assert message == '\033[93mNodimoWarning\033[0m: nodimo warning message\n' 


def test_show_nodimo_warning():
    with catch_warnings(record=True) as w:
        _show_nodimo_warning('nodimo warning message')
        assert len(w) == 1
        assert issubclass(w[-1].category, NodimoWarning)
        assert str(w[-1].message) == 'nodimo warning message'
