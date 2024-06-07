#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Internal
========

This module contains variables and functions for internal use.

Variables
---------
_is_running_on_jupyter : bool
    If ``True``, the package in running on IPython/Jupyter.

Functions
---------
_custom_display(obj)
    Displays object using a custom CSS style.
_show_object(obj, use_custom_css=True)
    Prints object in shell.
_print_horizontal_line()
    Prints a horizontal line.
_show_nodimo_warning(message)
    Displays a NodimoWarning message with custom format.

Classes
-------
NodimoWarning
    (Custom) Nodimo warning
"""

from sympy import pretty, Number, ImmutableDenseMatrix, sympify, nsimplify
from typing import Union
import warnings


# Determine if Nodimo is running on IPython/Jupyter.
try:
    from IPython import get_ipython

    _is_running_on_jupyter = True if get_ipython() is not None else False
    if not _is_running_on_jupyter:
        raise
    from IPython.display import display, Markdown, HTML
except:
    _is_running_on_jupyter = False


def _custom_display(obj):
    """Displays object using a custom CSS style.

    This custom display function was created to avoid vertical scrolling
    bars on the right of cells outputs, specially when running jupyter
    notebook in Google Chrome (issue #10 on github repository).

    Parameters
    ----------
    obj : Any
        The object to print.
    """

    css_style = ('<style>.jp-OutputArea-output{'
        'overflow-y: hidden;'
    '}</style>')

    display(HTML(css_style + f'${obj._repr_latex_()}$'))


def _show_object(obj, use_custom_css=True):
    """Prints object in shell.

    Parameters
    ----------
    obj : Any
        The object to print.
    use_custom_css : bool, default=True
        If ``True``, the object is displayed using custom css.
    """

    if _is_running_on_jupyter:
        if use_custom_css:
            _custom_display(obj)
        else:
            display(obj)
    else:
        print('\n' + pretty(obj) + '\n')  # TODO: root_notation=False was removed. Check if it will affect the diplay.


def _print_horizontal_line():
    if _is_running_on_jupyter:
        display(Markdown('<hr>'))
    else:
        print(78 * '-')


def _sympify_number(number: Union[int, float, str, tuple]) -> Number:
    """Converts a number representation into a Sympy number.

    This method is roughly a wrapper for Sympy.sympify, but it only
    accepts objects that can be transformed into a Sympy number. A
    workaround was implemented to allow the creation of rational numbers
    from tuples.

    Parameters
    ----------
    number : Union[int, float, str, tuple]
        Anything that represents a number.

    Returns
    -------
    number_sp : Number
        The input number converted to a Sympy number.

    Raises
    ------
    ValueError
        If the input could not be converted into a Sympy number.
    
    Examples
    --------

    >>> from nodimo._internal import _sympify_number as spnum
    >>> from sympy import Integer, Rational
    >>> spnum(5) == spnum(5.0) == spnum('5') == Integer(5)
    >>> spnum((2,3)) == spnum(2/3) == spnum('2/3') == Rational(2,3)
    """

    if hasattr(number, 'is_number') and number.is_number:
        return number

    try:
        number_sp = sympify(number)

        if number_sp.is_Rational:
            return number_sp
        elif number_sp.is_Float:
            number_sp_rational = nsimplify(number_sp, rational=True)
            if number_sp_rational.denominator <= 100:
                return number_sp_rational
            else:
                return number_sp
        elif isinstance(number, tuple) and len(number) in {1,2}:
            if all(obj.is_Number for obj in number_sp):
                return Number(*number_sp)
        elif number_sp.is_number:
            return number_sp

        raise
    except:
        raise ValueError(f"{repr(number)} could not be converted to a Sympy number")


def _unsympify_number(number_sp: Number) -> Union[int, float, str, tuple]:
    """Does the inverse of _sympify_number.

    Parameters
    ----------
    number_sp : Number
        The Sympy number.

    Returns
    -------
    number : Union[int, float, str, tuple]
        Any expression that represents a number.

    Raises
    ------
    ValueError
        If the input is not a Sympy Number.
    """

    if not hasattr(number_sp, 'is_number') or not number_sp.is_number:
        raise ValueError(f"{repr(number_sp)} is not a Sympy number")
    elif number_sp.is_Integer:
        return int(number_sp)
    elif number_sp.is_Rational:
        return (int(number_sp.numerator), int(number_sp.denominator))
    elif number_sp.is_Float:
        return float(number_sp)
    else:
        return str(number_sp)


def _sequence_to_matrix(sequence: list[list[Number]]) -> ImmutableDenseMatrix:
    """Converts a list of lists of numbers to a Sympy matrix.

    Parameters
    ----------
    sequence : list[list[Number]]
        Sequence that represents a matrix.

    Returns
    -------
    matrix : ImmutableDenseMatrix
        The original sequence converted to a Sympy matrix.

    Raises
    ------
    TypeError
        If the input is not a list of lists of numbers.
    """

    if hasattr(sequence, 'is_Matrix') and sequence.is_Matrix:
        return sequence.as_immutable
    elif not isinstance(sequence, (list, tuple)):
        raise TypeError(f"{sequence} is not a list of lists of numbers")

    sequence_sp = []
    for row in sequence:
        if isinstance(row, (list, tuple)):
            row_sp = []
            for e in row:
                row_sp.append(_sympify_number(e))
            sequence_sp.append(row_sp)
        else:
            sequence_sp.append(_sympify_number(row))
    
    matrix = ImmutableDenseMatrix(sequence_sp)

    return matrix


class NodimoWarning(Warning):
    """(Custom) Nodimo warning.

    Issued anytime Nodimo finds an inconsistency in the user's input,
    but one that can be handled without halting the execution.
    """

    pass


def _nodimo_formatwarning(message, category, filename, lineno, line=None):
    return f'\033[93m{category.__name__}\033[0m: {message}\n'


warnings.formatwarning = _nodimo_formatwarning  # TODO: Check if this does not impact other warning messages.


def _show_nodimo_warning(message: str):
    warnings.warn(message, NodimoWarning)
