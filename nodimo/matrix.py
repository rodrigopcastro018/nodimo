"""
=============================
Matrix (:mod:`nodimo.matrix`)
=============================

This module contains the class to create a dimensional matrix.

Classes
-------
DimensionalMatrix
    Creates a dimensional matrix from a given set of variables.
"""

import sympy as sp
from sympy import Matrix
from sympy.core._print_helpers import Printable
from typing import Union

from nodimo.variable import Variable
from nodimo.group import VariableGroup
from nodimo._internal import (_show_object,
                              _obtain_dimensions,
                              _build_dimensional_matrix)


# Aliases for types used in ModelFunction.
VariableOrGroup = Union[Variable, VariableGroup]
SeparatedVariablesTuple = tuple[VariableOrGroup, list[VariableOrGroup]]


class DimensionalMatrix(Printable):
    """Creates a dimensional matrix from a given set of variables.

    A DimensionalMatrix is a matrix with one column for each variable,
    one row for each dimension, and every element represents the
    dimension's exponent of a particular variable. It inherits from the
    Sympy Printable class the ability to be displayed on screen in a
    pretty format.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the dimensional matrix.
    dimensions : list[str], default=[]
        List with the dimensions' names of the given variables.

    Attributes
    ----------
    variables : list[Variable]
        List with the variables used to build the dimensional matrix.
    dimensions : list[str]
        List with the dimensions' names of the given variables.
    matrix : Matrix
        Dimensional matrix containing only the dimensions' exponents.
    labeled_matrix : Matrix
        Dimensional matrix labeled with variables and dimensions.
    latex : str
        String that represents the labeled dimensional matrix in latex.
    rank_ : int
        The rank of the dimensional matrix.

    Methods
    -------
    show()
        Displays the labeled dimensional matrix.

    Examples
    --------
    Consider the dimensions mass ``M``, length ``L`` and time ``T``.
    Next, assuming that ``x`` is displacement, ``k`` is stiffness and
    ``F`` is force, the dimensional matrix ``dmatrix`` for these three
    variables is built and displayed as:

    >>> from nodimo import Variable, DimensionalMatrix
    >>> F = Variable('F', M=1, L=1, T=-2)
    >>> k = Variable('m', M=1, T=-2)
    >>> x = Variable('a', L=1)
    >>> dmatrix = DimensionalMatrix(F, k, x)
    >>> dmatrix.show()
    """

    def __init__(self, *variables: Variable, dimensions: list[str] = []):

        if dimensions == []:
            dimensions = _obtain_dimensions(*variables)

        self.dimensions: list[str] = dimensions
        self.variables: list[Variable] = list(variables)
        self.matrix: Matrix = _build_dimensional_matrix(list(variables),
                                                        dimensions)
        self.labeled_matrix: Matrix = self._build_labeled_matrix()
        self.latex: str = self._build_latex_representation()
        self.rank: int = self.matrix.rank()

    def _build_labeled_matrix(self) -> Matrix:
        """Builds the labeled dimensional matrix.

        Returns
        -------
        labeled_matrix : Matrix
            Dimensional matrix labeled with the constitutive variables
            on the top row and the dimensions on the left column.
        """

        labeled_matrix = self.matrix.copy()
        dimensions_matrix = sp.Matrix(self.dimensions)
        variables_matrix = sp.Matrix([Variable('')] + self.variables).T
        labeled_matrix = labeled_matrix.col_insert(0, dimensions_matrix)
        labeled_matrix = labeled_matrix.row_insert(0, variables_matrix)

        return labeled_matrix

    def _build_latex_representation(self) -> str:
        """Builds the labeled dimensional matrix in latex.

        Returns
        -------
        latex_representation : str
            Latex string that represents the dimensional matrix labeled
            with the constitutive variables on the top row and the
            dimensions on the left column.
        """

        latex_representation = R'\begin{array}'
        latex_representation += '{r|' + 'r' * len(self.variables) + '} & '
        latex_representation += ' & '.join([sp.latex(var)
                                            for var in self.variables])
        latex_representation += R'\\ \hline '

        for i, dim in enumerate(self.dimensions):
            dimension_latex = [sp.latex(dim)]

            exponents_latex = []
            for exp in self.matrix[i, :]:
                if exp < 0:
                    exponents_latex.append(sp.latex(exp))
                else:
                    # Mimic the minus sign to preserve column width.
                    exponents_latex.append(R'\phantom{-}' + sp.latex(exp))

            dimension_and_exponents_latex = ' & '.join(dimension_latex
                                                       + exponents_latex)

            latex_representation += dimension_and_exponents_latex + R'\\'

        latex_representation += R'\end{array}'

        return latex_representation
    
    def show(self) -> None:
        """Displays the labeled dimensional matrix."""

        _show_object(self)

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return sp.pretty(self.labeled_matrix, root_notation=False)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join([sp.srepr(var) for var in self.variables])

        if self.dimensions == _obtain_dimensions(*self.variables):
            dimensions_repr = ''
        else:
            dimensions_repr = f', dimensions=[{', '.join(
                [f"'{dim}'" for dim in self.dimensions]
            )}]'

        return (f'{class_name}('
                + variables_repr
                + dimensions_repr
                + ')')

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return self.latex


# Alias for DimensionalMatrix.
DimMatrix = DimensionalMatrix
