"""
=============================
Matrix (:mod:`nodimo.matrix`)
=============================

This module contains the classes to create a dimensional matrix.

Classes
-------
BasicDimensionalMatrix
    Creates a basic dimensional matrix from a group of variables.
DimensionalMatrix
    Creates a dimensional matrix from a group of variables.
"""

import sympy as sp
from sympy import ImmutableDenseMatrix
from typing import Optional

from nodimo.variable import BasicVariable
from nodimo.group import Group


class BasicDimensionalMatrix(Group):
    """Creates a basic dimensional matrix from a group of variables.

    A BasicDimensionalMatrix is a matrix with one column for each
    variable, one row for each dimension, and every element represents
    the dimension's exponent of a particular variable.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that constitute the dimensional matrix.
    dimensions : tuple[str], default=None
        List with the dimensions to be used in the dimensional matrix.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        List with the variables used to build the dimensional matrix.
    dimensions : tuple[str]
        List with the dimensions used in the dimensional matrix.
    matrix : ImmutableDenseMatrix
        Dimensional matrix containing only the dimensions' exponents.

    Methods
    -------
    show()
        Displays the basic dimensional matrix.
    """

    def __init__(
        self,
        *variables: BasicVariable,
        dimensions: Optional[tuple[str]] = None
    ):

        super().__init__(*variables)
        self._raw_matrix: list[list[int]]
        self._matrix: ImmutableDenseMatrix
        self._rank: int
        self._independent_rows: tuple[int]
        self._submatrices: dict[BasicVariable, ImmutableDenseMatrix] = {}

        if dimensions is not None:
            self.dimensions = dimensions

        self._set_basicmatrix_properties()

    @Group.variables.setter
    def variables(self, variables: tuple[BasicVariable]):
        self._variables = variables
        self._set_basicgroup_properties
        self._set_basicmatrix_properties()

    @Group.dimensions.setter
    def dimensions(self, dimensions: tuple[str]):
        self._dimensions = dimensions
        self._set_basicmatrix_properties()

    @property
    def matrix(self) -> ImmutableDenseMatrix:
        return self._matrix

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def independent_rows(self) -> tuple[int]:
        return self._independent_rows

    def _set_basicmatrix_properties(self):
        """Sets dimensional matrix properties."""

        self._build_matrix()

    def _build_matrix(self):
        """Builds a dimensional matrix from the variables."""
    
        raw_matrix = []
    
        for dim in self._dimensions:
            dim_exponents = []
            for var in self._variables:
                if dim in var.dimensions.keys():
                    dim_exponents.append(var.dimensions[dim])
                else:
                    dim_exponents.append(sp.S.Zero)
            raw_matrix.append(dim_exponents)

        self._raw_matrix = raw_matrix
        self._matrix = ImmutableDenseMatrix(raw_matrix)

    def _set_independent_rows(self):
        """Gets the indexes of the dimensional matrix independent rows."""

        self._rank = self._matrix.rank()
        
        if len(self._dimensions) > self._rank:
            _, independent_rows = self._matrix.T.rref()
        else:
            independent_rows = tuple(range(len(self._dimensions)))
        
        self._independent_rows = independent_rows

    def _build_submatrices(self):
        """Builds one column matrix for each variable."""

        submatrices = []
        for i, var in enumerate(self._variables):
            submatrices.append((var, self._matrix.col(i)))

        self._submatrices = dict(submatrices)

    def _get_submatrix(self, *variables) -> ImmutableDenseMatrix:
        """Combines the variables submatrices into one submatrix.

        Parameters
        ----------
        *variables : BasicVariable
            Variables used to build the submatrix.

        Returns
        -------
        submatrix : ImmutableDenseMatrix
            The submatrix built from the given variables.

        Raises
        ValueError
            If the given variables are not all part of the dimensional matrix.
        """

        if not set(variables).issubset(set(self._variables)):
            raise ValueError(f"'{variables}' is not a subset of '{self._variables}'")
        elif self._submatrices == {}:
            self._build_submatrices()

        submatrices = [self._submatrices[var] for var in variables]
        submatrix = ImmutableDenseMatrix.hstack(*submatrices)

        return submatrix

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return sp.pretty(self._matrix, root_notation=False)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = sp.srepr(self._variables)[1:-1]

        if self._dimensions == Group(*self._variables)._dimensions:
            dimensions_repr = ''
        else:
            dimensions_repr = f', dimensions={self._dimensions}'

        return (f'{class_name}('
                + variables_repr
                + dimensions_repr
                + ')')

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return sp.latex(self._matrix, root_notation=False)


class DimensionalMatrix(BasicDimensionalMatrix):
    """Creates a dimensional matrix from a group of variables.

    Similar to a BasicDimensionalMatrix, but with labels at the side and
    at the top of the matrix to display the dimensions and variables.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that constitute the dimensional matrix.
    dimensions : tuple[str], default=None
        List with the dimensions to be used in the dimensional matrix.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        List with the variables used to build the dimensional matrix.
    dimensions : tuple[str]
        List with the dimensions used in the dimensional matrix.
    matrix : ImmutableDenseMatrix
        Dimensional matrix containing only the dimensions' exponents.
    labeled_matrix : ImmutableDenseMatrix
        Dimensional matrix labeled with variables and dimensions.
    rank : int
        The rank of the dimensional matrix.
    independent_rows : tuple[int]
        Indexes of the dimensional matrix independent rows.

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

    def __init__(
        self,
        *variables: BasicVariable,
        dimensions: Optional[tuple[str]] = None
    ):

        super().__init__(*variables, dimensions=dimensions)
        self._labeled_matrix: ImmutableDenseMatrix
        self._latex_repr: str
        self._set_matrix_properties()

    @BasicDimensionalMatrix.variables.setter
    def variables(self, variables: tuple[BasicVariable]):
        self._variables = variables
        self._set_basicgroup_properties()
        self._set_basicmatrix_properties()
        self._set_matrix_properties()

    @BasicDimensionalMatrix.dimensions.setter
    def dimensions(self, dimensions: list[str]):
        self._dimensions = dimensions
        self._set_basicmatrix_properties()
        self._set_matrix_properties()

    def _set_matrix_properties(self):
        """Sets dimensional matrix properties."""

        self._build_labeled_matrix()
        self._build_latex_repr()
        self._set_independent_rows()

    def _build_labeled_matrix(self):
        """Builds the labeled dimensional matrix."""

        labeled_matrix = self._matrix.as_mutable()
        dimensions_matrix = sp.Matrix(self._dimensions)
        variables_matrix = sp.Matrix([sp.Symbol('')] + list(self._variables)).T
        labeled_matrix = labeled_matrix.col_insert(0, dimensions_matrix)
        labeled_matrix = labeled_matrix.row_insert(0, variables_matrix)

        self._labeled_matrix = labeled_matrix.as_immutable()

    def _build_latex_repr(self):
        """Builds the labeled dimensional matrix in latex format.

        Notes
        -----
        Do not confuse the private attribute _latex_repr with the method
        _latex_repr_ inherited from the sympy Printable class.
        """

        latex_repr = R'\begin{array}'
        latex_repr += '{r|' + 'r' * len(self._variables) + '} & '
        latex_repr += ' & '.join([sp.latex(var) for var in self._variables])
        latex_repr += R'\\ \hline '

        for i, dim in enumerate(self._dimensions):
            dim_latex = [sp.latex(dim)]
            exp_latex = []
            for exp in self._matrix[i, :]:
                if exp < 0:
                    exp_latex.append(sp.latex(exp))
                else:
                    # Mimic the minus sign to preserve column width.
                    exp_latex.append(R'\phantom{-}' + sp.latex(exp))
            dim_and_exp_latex = ' & '.join(dim_latex + exp_latex)
            latex_repr += dim_and_exp_latex + R'\\'
        latex_repr += R'\end{array}'

        self._latex_repr = latex_repr

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return sp.pretty(self._labeled_matrix, root_notation=False)

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return self._latex_repr


# Alias for DimensionalMatrix.
DimMatrix = DimensionalMatrix
