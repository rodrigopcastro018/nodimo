"""This module contains functions that are used internally.

Variables
---------
_is_running_on_jupyter : bool
    If ``True``, the package in running on jupyter notebooks.
color_warning : str
    ANSI code for the warning message color.
color_end : str
    ANSI code to reset the color.

Functions
---------
_show_object(obj)
    Prints object in shell.
_print_horizontal_line()
    Prints a horizontal line.
_obtain_dimensions(*variables)
    Obtains the dimensions' names from the given variables.
_build_dimensional_matrix(variables, dimensions=[])
    Builds a basic dimensional matrix.
"""

import sympy as sp
from sympy import Matrix
from typing import Any
from nodimo.variable import Variable


_is_running_on_jupyter: bool

try:
    from IPython import get_ipython

    _is_running_on_jupyter = True if get_ipython() is not None else False
    if not _is_running_on_jupyter:
        raise
    from IPython.display import display, Markdown, HTML
except:
    _is_running_on_jupyter = False


# ANSI color codes
color_warning: str = '\033[93m'
color_end: str = '\033[0m'


def _custom_display(obj: Any) -> None:
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


def _show_object(obj: Any, use_custom_css: bool = True) -> None:
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
        print()
        sp.pprint(obj, root_notation=False)
        print()


def _print_horizontal_line() -> None:
    """Prints a horizontal line."""

    if _is_running_on_jupyter:
        display(Markdown('<hr>'))
    else:
        print(78 * '-')


def _remove_duplicates(original_list: list) -> list:
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


def _obtain_dimensions(*variables: Variable) -> list[str]:
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

    # Eliminate duplicates but keep order.
    dimensions = sorted(set(dimensions), key=dimensions.index)

    return dimensions


def _build_dimensional_matrix(variables: list[Variable],
                              dimensions: list[str] = []) -> Matrix:
    """Builds a basic dimensional matrix.

    A basic dimensional matrix contains only numbers, no labels.

    Parameters
    ----------
    variables : list[Variable]
        List with the variables used to build the dimensional matrix.
    dimensions : list[str], default=[]
        List with the dimensions' names of the given variables. If not
        provided, this list is obtained from the variables.

    Returns
    -------
    dimensional_matrix : Matrix
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

    return dimensional_matrix
