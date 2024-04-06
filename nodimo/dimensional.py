"""
=============================================
Dimensional Model (:mod:`nodimo.dimensional`)
=============================================

This module contains the class to create a dimensional model.

Classes
-------
DimensionalModel
    Creates a dimensional model from a given set of variables.
"""

import numpy as np
import sympy as sp

from nodimo.basic import BasicVariable, Basic
from nodimo.matrix import DimensionalMatrix
from nodimo.function import ModelFunction
from nodimo._internal import (color_warning, color_end,
                              _show_object,
                              _build_dimensional_matrix)


# Alias for type used in DimensionalModel.
OrganizedVariablesTuple = tuple[list[BasicVariable], list[BasicVariable],
                                list[BasicVariable], list[BasicVariable]]


class DimensionalModel(Basic):
    """Creates a dimensional model from a given set of variables.

    This class is a base step in the construction of the nondimensional
    models. A dimensional model states a relationship between variables,
    and this relationship is represented by the dimensional function.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the model.
    check_variables : bool, defaul=True
        If ``True``, extra variables and dimensions are searched.
    display_messages : bool, default=True
        If ``True``, extra variables and dimensions are displayed.

    Attributes
    ----------
    variables : list[Variable]
        List of variables that compose the model.
    dimensions : list[str]
        List with the dimensions' names of the given variables.
    dimensional_variables : list[Variable]
        List of dimensional variables.
    nondimensional_variables : list[Variable]
        List of nondimensional variables.
    scaling_variables : list[Variable]
        List of scaling variables.
    nonscaling_variables : list[Variable]
        List of nonscaling variables.
    dimensional_matrix : DimensionalMatrix
        Dimensional matrix for the given set of variables.
    dimensional_function : ModelFunction
        Function that represents the dimensional model.

    Methods
    -------
    build_dimensional_model() = build()
        Builds the main characteristics of the dimensional model.
    search_extra_variables_and_dimensions(display_messages=True)
        Searchs for extra variables and dimensions.
    show_dimensional_model() = show()
        Displays the dimensional model.

    Raises
    ------
    ValueError
        If the number of effective variables is lower than two.
        
    Examples
    --------
    * Simple Pendulum

    Consider the dimensions mass ``M``, length ``L`` and time ``T``.
    Next, assuming that ``P`` is period, ``m`` is mass and, ``g`` is
    gravitational acceleration, ``R`` is the pendulum's length and
    ``t0`` is the initial angle, the dimensional model ``dmodel`` for
    the period is built and shown as:

    >>> from nodimo import Variable, DimensionalModel
    >>> P = Variable('P', T=1, dependent=True)
    >>> m = Variable('m', M=1)
    >>> g = Variable('g', L=1, T=-2, scaling=True)
    >>> R = Variable('R', L=1, scaling=True)
    >>> t0 = Variable('theta0')
    >>> dmodel = DimensionalModel(P, m, g, R, t0)
    >>> dmodel.show()
    """

    def __init__(self,
                 *variables: BasicVariable,
                 check_variables: bool = True,
                 display_messages: bool = True):

        self.variables: list[BasicVariable]
        self.dimensions: list[str]
        super().__init__(*variables)

        self.dimensional_variables: list[BasicVariable]
        self.nondimensional_variables: list[BasicVariable]
        self.scaling_variables: list[BasicVariable]
        self.nonscaling_variables: list[BasicVariable]

        self.dimensional_matrix: DimensionalMatrix
        self.dimensional_function: ModelFunction

        if check_variables:
            self.search_extra_variables_and_dimensions(display_messages)

        if len(self.variables) < 2:
            raise ValueError("The model must have at least two variables")

        (
            self.dimensional_variables,
            self.nondimensional_variables,
            self.scaling_variables,
            self.nonscaling_variables
        ) = self._organize_variables()

        self.build_dimensional_model()

    def build_dimensional_model(self) -> None:
        """Builds the main characteristics of the dimensional model."""

        self.dimensional_matrix = DimensionalMatrix(*self.variables,
                                                    dimensions=self.dimensions)
        
        self.dimensional_function = ModelFunction(*self.variables, name='pi')

    # Alias for build_dimensional_model.
    build = build_dimensional_model

    def search_extra_variables_and_dimensions(
            self, display_messages: bool = True) -> None:
        """Searchs for extra variables and dimensions.

        Parameters
        ----------
        display_messages : bool, default=True
            If ``True``, extra variables and dimensions are displayed.
        """

        dimensional_matrix_sp = _build_dimensional_matrix(self.variables,
                                                          self.dimensions)
        
        dimensional_matrix_bool = np.array(dimensional_matrix_sp, dtype=bool)

        extra_variables = []
        extra_dimensions = []

        for dim, row in zip(self.dimensions, dimensional_matrix_bool):
            if np.sum(row) == 1:
                var = self.variables[np.where(row == 1)[0][0]]
                extra_variables.append(var)
                extra_dimensions.append(dim)
            if np.sum(row) == 0:
                extra_dimensions.append(dim)

        for var in extra_variables:
            self.variables.remove(var)

        for dim in extra_dimensions:
            self.dimensions.remove(dim)

        if display_messages:
            if len(extra_variables) > 0:
                print(color_warning
                      + "Variables that can not be part of the model:"
                      + color_end)
                print(color_warning
                      + '    ' + sp.pretty(extra_variables)[1:-1]
                      + color_end)

            if len(extra_dimensions) > 0:
                print(color_warning
                      + "Dimensions that can not be part of the model:"
                      + color_end)
                print(color_warning
                      + '    ' + sp.pretty(extra_dimensions)[1:-1]
                      + color_end)

    def _organize_variables(self) -> OrganizedVariablesTuple:
        """Organizes the variables according to their types.

        The variables are organized into dimensional and nondimensional.
        The dimensional category is further subdivided into scaling and
        nonscaling variables.

        Returns
        -------
        dimensional_variables : list[Variable]
            List of dimensional variables.
        nondimensional_variables : list[Variable]
            List of nondimensional variables.
        scaling_variables : list[Variable]
            List of scaling variables.
        nonscaling_variables : list[Variable]
            List of nonscaling variables.
        """

        dimensional_variables = []
        nondimensional_variables = []
        scaling_variables = []
        nonscaling_variables = []

        for var in self.variables:
            if var.is_nondimensional:
                nondimensional_variables.append(var)
            else:
                if var.is_scaling:
                    scaling_variables.append(var)
                else:
                    nonscaling_variables.append(var)

        # Store dimensional variables in order.
        dimensional_variables = nonscaling_variables + scaling_variables

        return (dimensional_variables,
                nondimensional_variables,
                scaling_variables,
                nonscaling_variables)

    # Created this method so the dimensional model can be displayed from
    # the nondimensional models.
    def show_dimensional_model(self) -> None:
        """Displays the dimensional model."""

        self.dimensional_function.show()

    def __eq__(self, other) -> bool:
        
        if self is other:
            return True
        elif not isinstance(other, type(self)):
            return False
        elif set(self.variables) != set(other.variables):
            return False
        
        return True

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return sp.sstr(self.dimensional_function)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join([sp.srepr(var) for var in self.variables])

        return (f'{class_name}('
                + variables_repr
                + ')')

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return sp.latex(self.dimensional_function)


# Alias for the class DimensionalModel.
DimModel = DimensionalModel
