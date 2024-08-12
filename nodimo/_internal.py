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
_sympify_number(number)
    Converts a number representation into a Sympy number.
_unsympify_number(number)
    Does the inverse of _sympify_number.
_prettify_name(name, bold=True)
    Wrapper for the Sympy function pretty_symbol.
_show_nodimo_warning(message)
    Displays a NodimoWarning message with custom format.

Classes
-------
NodimoWarning
    (Custom) Nodimo warning
"""

from sympy import pretty, Number, Rational, nsimplify, sympify
from sympy.printing.pretty.pretty_symbology import pretty_symbol
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

    css_style = '<style>.jp-OutputArea-output{overflow-y: hidden;}</style>'

    display(HTML(css_style + f'${obj._repr_latex_()}$'))


def _show_object(obj, use_custom_css=True, use_unicode=True):
    """Prints object in shell.

    Parameters
    ----------
    obj : Any
        The object to print.
    use_custom_css : bool, default=True
        If ``True``, the object is displayed using custom css. Only
        available in IPython/Jupyter.
    use_unicode : bool, default=False
        If ``True``, the object is displayed using unicode characters.
        Only available for pretty printing.
    """

    if _is_running_on_jupyter:
        if use_custom_css:
            _custom_display(obj)
        else:
            display(obj)
    else:
        print('\n' + pretty(obj, use_unicode=use_unicode) + '\n')


def _print_horizontal_line():
    """Prints a horizontal line in shell."""

    if _is_running_on_jupyter:
        display(Markdown('<hr>'))
    else:
        print(78 * '-')


def _sympify_number(number: Union[int, float, str, tuple, Number]) -> Number:
    """Converts a number representation into a Sympy number.

    This method is roughly a wrapper for Sympy.sympify, but it only
    accepts objects that can be transformed into a Sympy number. A
    workaround was implemented to allow the creation of rational numbers
    from tuples.

    Parameters
    ----------
    number : Union[int, float, str, tuple, Number]
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

    number_sp = sympify(number)

    if number_sp.is_Rational:
        return number_sp
    elif number_sp.is_Float and not isinstance(number, Number):
        number_sp_rational = nsimplify(number_sp, rational=True)
        denattr = number_sp_rational.denominator
        number_denominator = denattr if not callable(denattr) else denattr()
        if number_denominator <= 100:
            return number_sp_rational
        else:
            return number_sp
    elif isinstance(number, tuple) and len(number) in {1, 2}:
        if all(obj.is_Number for obj in number_sp):
            return Number(*number_sp)
    elif number_sp.is_number:
        return number_sp

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
        number_rat: Rational = Rational(number_sp)
        numattr = number_rat.numerator
        denattr = number_rat.denominator
        number_numerator = numattr if not callable(numattr) else numattr()
        number_denominator = denattr if not callable(denattr) else denattr()
        return (int(number_numerator), int(number_denominator))
    elif number_sp.is_Float:
        return float(number_sp)
    else:
        return str(number_sp)


def _prettify_name(name: str, bold: bool = False):
    """Wrapper for the Sympy function pretty_symbol.

    This function was created to provide a better exception context for
    the Sympy function pretty_symbol.

    Parameters
    ----------
    name : str
        String to be prettified.
    bold : bool, default=False
        If ``True``, the string is converted to boldface. Only availabe
        for non-numeric values.

    Returns
    -------
    pretty_name : str
        Prettified string

    Raises
    ------
    ValueError
        If the input name is invalid.
    """

    try:
        return pretty_symbol(name, bold_name=bold)
    except:
        raise ValueError(f"{repr(name)} is an invalid name")


class NodimoWarning(Warning):
    """(Custom) Nodimo warning.

    Issued anytime Nodimo finds an inconsistency in the user's input,
    but one that can be handled without halting the execution.
    """

    pass


def _nodimo_formatwarning(message, category, filename, lineno, line=None):
    return f'\033[93m{category.__name__}\033[0m: {message}\n'


def _show_nodimo_warning(message: str):
    """Displays a NodimoWarning message with custom formattting.

    Parameters
    ----------
    message : str
        The message to be displayed in the warning.
    """

    original_formatwarning = warnings.formatwarning
    warnings.formatwarning = _nodimo_formatwarning
    warnings.warn(message, NodimoWarning)
    warnings.formatwarning = original_formatwarning
