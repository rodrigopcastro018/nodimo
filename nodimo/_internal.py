"""This module contains variables and functions for internal use.

Variables
---------
_is_running_on_jupyter : bool
    If ``True``, the package in running on jupyter notebooks.

Functions
---------
_show_object(obj)
    Prints object in shell.
_print_horizontal_line()
    Prints a horizontal line.
_print_warning(message)
    Prints a message with warning colors.
_remove_duplicates(original_list)
    Removes duplicates from a list, keeping the order.
_obtain_dimensions(*variables)
    Obtains the dimensions' names from the given variables.
_build_dimensional_matrix(variables, dimensions=[])
    Builds a basic dimensional matrix.
"""

import sympy as sp  # TODO: Remove this later
from sympy import Rational, pretty, sympify, nsimplify
from typing import Union
import warnings

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
        print('\n' + pretty(obj, root_notation=False) + '\n')


def _print_horizontal_line():
    """Prints a horizontal line."""

    if _is_running_on_jupyter:
        display(Markdown('<hr>'))
    else:
        print(78 * '-')


def _sympify_number(number: Union[int, float, str, tuple]) -> Rational:
    """Converts a number representation into a Sympy number.

    This method is roughly a wrapper for Sympy.sympify, but it only
    accepts and returns number objects. A workaround was implemented to
    allow the creation of rational numbers from tuples.

    Parameters
    ----------
    number : Union[int, str, tuple]
        Any expression that represents a number.

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
    True
    >>> spnum((2,3)) == spnum(2/3) == spnum('2/3') == Rational(2,3)
    True
    """

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
        if all(obj.is_number for obj in number_sp):
            return Rational(*number_sp)
    elif number_sp.is_number:
        return number_sp

    raise ValueError(f"'{number}' could not be converted to a Sympy number")


def _unsympify_number(number_sp: Rational) -> Union[int, str, tuple]:
    """Does the inverse of _sympify_number.

    Parameters
    ----------
    number_sp : Number
        The input number converted to a Sympy number.

    Returns
    -------
    number : Union[int, str, tuple]
        Any expression that represents a number.

    Raises
    ------
    ValueError
        If the input is not a sympy Number.
    """

    if not number_sp.is_number:
        raise ValueError(f"'{number_sp}' is not a Sympy number")
    elif number_sp.is_Integer:
        return int(number_sp)
    elif number_sp.is_Rational:
        return (int(number_sp.numerator), int(number_sp.denominator))
    else:
        return str(number_sp)


def _remove_duplicates(original_list):
    """Removes duplicates from a list, keeping the order.

    Parameters
    ----------
    original_list : list
        List to be checked for duplicates.

    Returns
    -------
    new_list : list
        List with duplicates removed.
    """

    new_list = []
    for e in original_list:
        if e not in new_list:
            new_list.append(e)

    return new_list


def _obtain_dimensions(*variables):
    """Obtains the dimensions' names from the given variables.

    Parameters
    ----------
    *variables : Variable
        Variables to get the dimensions extracted.

    Returns
    -------
    dimensions : list[str]
        List containing the dimensions' names.
    """

    dimensions = []

    for var in variables:
        dimensions += list(var.dimensions.keys())

    dimensions = _remove_duplicates(dimensions)

    return dimensions


def _build_dimensional_matrix(variables, dimensions=[], return_raw=False):
    """Builds a basic dimensional matrix.

    A basic dimensional matrix contains only numbers, no labels.

    Parameters
    ----------
    variables : list[Variable]
        List with the variables used to build the dimensional matrix.
    dimensions : list[str], default=[]
        List with the dimensions' names of the given variables. If not
        provided, this list is obtained from the variables.
    return_raw : bool, defaul=True
        If ``True``, return matrix will be a list of lists.

    Returns
    -------
    dimensional_matrix : Matrix or list[list[int]]
        Matrix with one column for each variable, one row for each
        dimension, and every entry represents the dimension's exponent
        of a particular variable.
    """

    if len(variables) > 0 and dimensions == []:
        dimensions = _obtain_dimensions(*variables)

    raw_dimensional_matrix = []

    for dim in dimensions:
        dimension_exponents = []

        for var in variables:
            if dim in var.dimensions.keys():
                dimension_exponents.append(var.dimensions[dim])
            else:
                dimension_exponents.append(0)

        raw_dimensional_matrix.append(dimension_exponents)

    dimensional_matrix = sp.Matrix(raw_dimensional_matrix)
    dimensional_matrix = sp.nsimplify(dimensional_matrix,
                                      rational=True).as_mutable()

    if return_raw:
        return raw_dimensional_matrix
    else:
        return dimensional_matrix


class UnrelatedVariableWarning(Warning):
    """Unrelated variable warning.
    
    Issued when a variable can not be used and, therefore, is discarded.
    """

    pass


warnings.simplefilter('always', UnrelatedVariableWarning)


def custom_formatwarning(message, category, filename, lineno, line=None):
    """Custom format for warning messages."""
    
    return f'\033[93m{category.__name__}\033[0m: {message}\n'


warnings.formatwarning = custom_formatwarning


def _show_warning(message: str, category: Warning):
    """Displays a message with warning colors."""

    warnings.warn(message, category)
