"""This module contains the class to create a dimensional matrix.

Classes
-------
DimensionalMatrix = DimMatrix
    Creates a dimensional matrix from a given set of variables.
"""

import sympy as sp
from sympy import Matrix
from typing import Union

from nodimo._internal import (_is_running_on_jupyter,
                              _show_object,
                              _obtain_dimensions,
                              _build_dimensional_matrix)

from .variable import Variable
from .group import VariableGroup


# Aliases for types used in ModelFunction.
VariableOrGroup = Union[Variable, VariableGroup]
SeparatedVariablesTuple = tuple[VariableOrGroup, list[VariableOrGroup]]


class DimensionalMatrix(Matrix):
    """Creates a dimensional matrix from a given set of variables.

    A DimensionalMatrix, on creation, is a basic dimensional matrix with
    one column for each variable, one row for each dimension, and every
    element represents the dimension's exponent of a singular variable.
    On initialization, this class also adds attributes that complement
    the way an instance of this object can be presented on screen, by
    inserting labels for its variables and dimensions.

    Attributes
    ----------
    variables: list[Variable]
        List with the variables used to build the dimensional matrix.
    dimensions: list[str]
        List with the dimensions' names of the given variables.
    labeled_matrix: Matrix
        Dimensional matrix labeled with variables and dimensions.
    latex: str
        String that represents the labeled dimensional matrix in latex.
    rank_: int
        The rank of the dimensional matrix.

    Methods
    -------
    build_labeled_matrix()
        Builds the labeled dimensional matrix.
    build_latex_representation()
        Builds the labeled dimensional matrix in latex.
    show()
        Displays the labeled dimensional matrix.

    Alias
    -----
    DimMatrix

    Examples
    -------
    Hooke's law:
    First, consider the dimensions mass (M), length (L) and time (T).
    Second, assuming that x is displacement, k is stiffness and F is
    force, the dimensional matrix (DM) for these three variables is
    built and displayed as:
    >>> from nodimo import Variable, DimensionalMatrix
    >>> F = Variable('F', M=1, L=1, T=-2)
    >>> k = Variable('m', M=1, T=-2)
    >>> x = Variable('a', L=1)
    >>> DM = DimensionalMatrix(F, k, x)
    >>> DM.show()
    """

    def __new__(cls, *variables: Variable, dimensions: list[str] = []):
        
        dimensional_matrix = _build_dimensional_matrix(list(variables),
                                                       dimensions)
        
        return super().__new__(cls, dimensional_matrix)

    def __init__(self, *variables: Variable, dimensions: list[str] = []):
        """
        Parameters
        ----------
        *variables: Variable
            Variables that constitute the dimensional matrix.
        dimensions: list[str]
            List with the dimensions' names of the given variables.
        """

        if dimensions == []:
            dimensions = _obtain_dimensions(*variables)

        self.dimensions: list[str] = dimensions
        self.variables: list[Variable] = list(variables)
        self.labeled_matrix: Matrix = self.build_labeled_matrix()
        self.latex: str = self.build_latex_representation()
        self.rank_: int = self.rank()  # To not override the rank method

    def build_labeled_matrix(self) -> Matrix:
        """Builds the labeled dimensional matrix.

        Returns
        -------
        labeled_matrix: Matrix
            Dimensional matrix labeled with the constitutive variables
            on the top row and the dimensions on the left column.
        """

        labeled_matrix = sp.Matrix(self)
        dimensions_matrix = sp.Matrix(self.dimensions)
        variables_matrix = sp.Matrix([Variable('')] + self.variables).T
        labeled_matrix = labeled_matrix.col_insert(0, dimensions_matrix)
        labeled_matrix = labeled_matrix.row_insert(0, variables_matrix)

        return labeled_matrix

    def build_latex_representation(self) -> str:
        """Builds the labeled dimensional matrix in latex.

        Returns
        -------
        latex_representation: str
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
            for exp in self[i, :]:
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

        dimensional_matrix: Union[str, Matrix]

        if _is_running_on_jupyter:
            dimensional_matrix = self.latex
        else:
            dimensional_matrix = self.labeled_matrix

        _show_object(dimensional_matrix)


# Alias for DimensionalMatrix.
DimMatrix = DimensionalMatrix