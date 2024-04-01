"""
=======================================
Model Function (:mod:`nodimo.function`)
=======================================

This module contains the class to creates model functions.

Classes
-------
ModelFunction
    Creates a function that relates a set of variables or groups.
"""

import sympy as sp
from sympy import Equality
from typing import Union

from nodimo.variable import Variable
from nodimo.group import VariableGroup
from nodimo._internal import _is_running_on_jupyter, _show_object


# Aliases for types used in ModelFunction.
VariableOrGroup = Union[Variable, VariableGroup]
SeparatedVariablesTuple = tuple[VariableOrGroup, list[VariableOrGroup]]


class ModelFunction(Equality):
    """Creates a function that relates a set of variables or groups.

    This class states a function that represents a model, that is, it
    expresses a relationship between the variables or variable groups
    that constitute a model.

    Parameters
    ----------
    *variables : Variable or VariableGroup
        Variables or groups that constitute the function.
    name : str, default='f'
        Name of the function, traditionally a single letter.

    Attributes
    ----------
    variables : list[Variable or VariableGroup]
        List of variables or groups used in the function.
    name : str, default='f'
        Name of the function, traditionally a single letter.
    dependent_variable : Variable or VariableGroup
        Dependent variable or group.
    independent_variables : list[Variable or VariableGroup]
        List of independent variables or groups.

    Methods
    -------
    show()
        Displays the function.

    Raises
    ------
    ValueError
        If there is less or more than one dependent variable.

    Examples
    --------
    Consider the dimensions mass ``M``, length ``L`` and time ``T``.
    Next, assuming that ``F`` is force, ``m`` is mass and ``a`` is
    acceleration, the function ``h`` that relates these three variables
    is built and displayed as:

    >>> from nodimo import Variable, ModelFunction
    >>> F = Variable('F', M=1, L=1, T=-2, dependent=True)
    >>> m = Variable('m', M=1)
    >>> a = Variable('a', L=1, T=-2)
    >>> h = ModelFunction(F, m, a)
    >>> h.show()
    """

    def __new__(cls, *variables: VariableOrGroup, name: str = 'f'):
        (
            dependent_variable,
            independent_variables
        ) = cls._separate_variables(*variables)

        (
            independent_variables_function
        ) = sp.Function(name)(*independent_variables)

        return super().__new__(cls,
                               dependent_variable,
                               independent_variables_function,
                               evaluate=False)

    def __init__(self, *variables: VariableOrGroup, name: str = 'f'):

        self.variables: list[VariableOrGroup] = list(variables)
        self.name: str = name
        self.dependent_variable: VariableOrGroup
        self.independent_variables: list[VariableOrGroup]

        (
            self.dependent_variable,
            self.independent_variables
        ) = self._separate_variables(*self.variables)

    @classmethod
    def _separate_variables(
        cls, *variables: VariableOrGroup) -> SeparatedVariablesTuple:
        """Splits the list of variables in dependent and independent.

        Parameters
        ----------
        *variables : Variable or VariableGroup
            Variables or groups that constitute the function.

        Returns
        -------
        dependent_variable : Variable
            Dependent variable or group.
        independent_variables : list[Variable]
            List of independent variables or groups.

        Raises
        ------
        ValueError
            If there is less or more than one dependent variable.
        """

        dependent_variable = []
        independent_variables = []

        for var in variables:
            if var.is_dependent:
                dependent_variable.append(var)
            else:
                independent_variables.append(var)

        if len(dependent_variable) != 1:
            raise ValueError("There must be exactly one dependent variable")

        return dependent_variable[0], independent_variables

    def show(self) -> None:
        """Displays the function."""

        _show_object(self)

    def _sympyrepr(self, printer):
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join([sp.srepr(var) for var in self.variables])
        name_repr = f", name='{self.name}'" if self.name != 'f' else ''

        return (f'{class_name}('
                + variables_repr
                + name_repr
                + ')')
