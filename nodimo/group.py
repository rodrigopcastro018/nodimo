"""
====================================
Variable Group (:mod:`nodimo.group`)
====================================

This module contains the class to create a group of variables.

Classes
-------
VariableGroup
    Creates a product of variables, each raised to an exponent.
"""

import numpy as np
import sympy as sp
from sympy import Mul, Matrix
from typing import Union

from nodimo.variable import Variable
from nodimo._internal import _obtain_dimensions, _build_dimensional_matrix


# Alias for type used in VariableGroup.
ListOrMatrix = Union[list, Matrix]


class VariableGroup(Mul):
    """Creates a product of variables, each raised to an exponent.

    A VariableGroup consists of a product of instances of the class
    Variable, each instance raised to a particular exponent. The
    dimensional characteristics of this group of variables are evaluated
    and stored as attributes.

    Parameters
    ----------
    variables : list[Variable]
        List of variables that constitute the group.
    exponents : list or Matrix
        List or matrix containing each variable's exponent.
    check_inputs : bool, default=True
        If ``True``, variables and exponents are validated.
    check_dimensions : bool, default=True
        If ``True``, dimensional properties are evaluated.

    Attributes
    ----------
    variables : list[Variable]
        List of variables that constitute the group.
    exponents : Matrix
        Matrix containing each variable's exponent.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the group is dependent.
    is_nondimensional : bool
        If ``True``, the group is nondimensional.

    Raises
    ------
    TypeError
        If the type of ``exponents`` is not ``list`` or ``Matrix``.
    TypeError
        If the list of variables contains at least one not-Variable.
    ValueError
        If the number of variables is lower than two.
    ValueError
        If the numbers of variables and exponents do not match.
    ValueError
        If the exponents are not in a row matrix.
        
    Examples
    --------
    Consider the dimensions mass ``M``, length ``L`` and time ``T``.
    Next, assuming that ``V`` is velocity, ``D`` is characteristic
    length, ``rho`` is density and ``mu`` is dynamic viscosity, the
    Reynolds number ``Re`` is built as:

    >>> from nodimo import Variable, VariableGroup
    >>> rho = Variable('rho', M=1, L=-3)
    >>> V = Variable('V', L=1, T=-1)
    >>> D = Variable('D', L=1)
    >>> mu = Variable('mu', M=1, L=-1, T=-1)
    >>> Re = VariableGroup([rho, V, D, mu], [1, 1, 1, -1])
    """

    def __new__(cls,
                variables: list[Variable],
                exponents: ListOrMatrix,
                check_inputs: bool = True,
                check_dimensions: bool = True):

        exponents = cls._convert_exponents(exponents)

        if check_inputs:
            cls._validate_variables_and_exponents(variables, exponents)

        # Flattening exponents_list.
        exponents_list = cls._convert_exponents(exponents).tolist()
        exponents_list = [exp
                          for explist in exponents_list
                          for exp in explist]

        terms = [var**exp
                 for var, exp in zip(variables, exponents_list)]

        return super().__new__(cls, *terms)

    def __init__(self,
                 variables: list[Variable],
                 exponents: ListOrMatrix,
                 check_inputs: bool = True,
                 check_dimensions: bool = True):

        super().__init__()
        self.variables: list[Variable] = list(variables)
        self.exponents: Matrix = self._convert_exponents(exponents)

        # The group is dependent if it contains a dependent variable
        # with exponent.
        is_dependent = [var.is_dependent for var in variables]
        has_exponent = np.array(exponents, dtype=bool).reshape(-1)
        self.is_dependent: bool = any(
            np.logical_and(is_dependent, has_exponent)
        )

        self.dimensions: dict[str, int] = dict()
        self.is_nondimensional: bool = True

        if check_dimensions:
            self.is_nondimensional = all(var.is_nondimensional
                                         for var in self.variables)

            # If all variables are nondimensional, there is no need to
            # determine the dimensional properties.
            if not self.is_nondimensional:
                self._get_dimensions()

    @classmethod
    def _convert_exponents(cls, exponents: ListOrMatrix) -> Matrix:
        """Converts a container of type ``list`` to the type ``Matrix``.

        Parameters
        ----------
        exponents : list or Matrix
            A container with numbers.

        Returns
        -------
        new_exponents: Matrix
            The ``exponents`` container converted to ``Matrix`` type. If
            the original container is already of the type ``Matrix``, no
            conversion is done and ``new_exponents`` is equal to
            ``exponents``.

        Raises
        ------
        TypeError
            If the type of ``exponents`` is not ``list`` or ``Matrix``.
        """

        if not isinstance(exponents, (list, Matrix)):
            raise TypeError("exponents type must be list or sympy.Matrix")

        if isinstance(exponents, list):
            new_exponents = sp.Matrix([exponents])
            new_exponents = sp.nsimplify(new_exponents,
                                         rational=True).as_mutable()
        else:
            new_exponents = exponents

        return new_exponents

    @classmethod
    def _validate_variables_and_exponents(cls,
                                         variables: list[Variable],
                                         exponents: Matrix) -> None:
        """Validates provided variables and exponents.

        Parameters
        ----------
        variables: list[Variable]
            List of variables that constitute the group.
        exponents: Matrix
            List or matrix containing each variable's exponent.

        Raises
        ------
        TypeError
            If the list of variables contains at least one not-Variable.
        ValueError
            If the number of variables is lower than two.
        ValueError
            If the numbers of variables and exponents do not match.
        ValueError
            If the exponents are not in a row matrix.
        """
        
        if not all(isinstance(var, Variable) for var in variables):
            raise TypeError("All variables must be of type Variable")
        elif len(variables) < 2:
            raise ValueError("Group must have at least two variables")
        elif len(variables) != sp.Mul(*exponents.shape):
            raise ValueError("Number of variables and exponents must match")
        elif exponents.shape[0] != 1:
            raise ValueError("Exponents must be in a row matrix")

    def _get_dimensions(self) -> None:
        """Evaluates the dimensional properties of the group."""

        # First, get dimensions names.
        dimensions_names = _obtain_dimensions(*self.variables)

        # Second, get dimensions exponents.
        dimensional_matrix = _build_dimensional_matrix(self.variables,
                                                       dimensions_names)

        dimensions_exponents = dimensional_matrix * self.exponents.T

        # Third, combine names and exponents.
        self.dimensions = dict(zip(dimensions_names, dimensions_exponents))

        self.is_nondimensional = dimensions_exponents.is_zero_matrix


# Alias for VariableGroup.
VarGroup = VariableGroup
