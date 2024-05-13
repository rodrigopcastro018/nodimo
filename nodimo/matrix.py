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

from sympy import srepr, ImmutableDenseMatrix, Matrix, S, latex
from typing import Optional

from nodimo.variable import Variable
from nodimo.groups import PrintableGroup


class DimensionalMatrix(PrintableGroup):
    """Creates a dimensional matrix from a group of variables.

    Similar to a BasicDimensionalMatrix, but with labels at the side and
    at the top of the matrix to display the dimensions and variables.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the dimensional matrix.
    dimensions : tuple[str], default=None
        List with the dimensions to be used in the dimensional matrix.

    Attributes
    ----------
    variables : tuple[Variable]
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
        *variables: Variable,
        dimensions: Optional[tuple[str]] = None
    ):

        super(PrintableGroup, self).__init__(*variables)
        
        if dimensions is not None:
            self._dimensions = dimensions
        
        self._latex_repr: str
        self._set_matrix_properties()
        self._set_printgroup_properties()

    @property
    def matrix(self) -> ImmutableDenseMatrix:
        return self._matrix

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def independent_rows(self) -> tuple[int]:
        return self._independent_rows

    def _build_symbolic(self):
        """Builds symbolic representation in Sympy."""

        labeled_matrix = self._matrix.as_mutable()
        dimensions_matrix = Matrix(self._dimensions)
        variables_matrix = Matrix([[Variable('')] + list(self._variables)])
        labeled_matrix = labeled_matrix.col_insert(0, dimensions_matrix)
        labeled_matrix = labeled_matrix.row_insert(0, variables_matrix)

        self._symbolic = labeled_matrix.as_immutable()

    def _set_matrix_properties(self):
        """Sets dimensional matrix properties."""

        self._build_matrix()
        self._set_matrix_rank()
        self._set_matrix_independent_rows()
        self._build_latex_repr()

    def _build_latex_repr(self):
        """Builds the labeled dimensional matrix in latex format.

        Notes
        -----
        Do not confuse the private attribute _latex_repr with the method
        _latex_repr_ inherited from the sympy Printable class.
        """

        latex_repr = R'\begin{array}'
        latex_repr += '{r|' + 'r' * len(self._variables) + '} & '
        latex_repr += ' & '.join([latex(var) for var in self._variables])
        latex_repr += R'\\ \hline '

        for i, dim in enumerate(self._dimensions):
            dim_latex = [latex(dim)]
            exp_latex = []
            for exp in self._matrix[i, :]:
                if exp < 0:
                    exp_latex.append(latex(exp))
                else:
                    # Mimic the minus sign to preserve column width.
                    exp_latex.append(R'\phantom{-}' + latex(exp))
            dim_and_exp_latex = ' & '.join(dim_latex + exp_latex)
            latex_repr += dim_and_exp_latex + R'\\'
        latex_repr += R'\end{array}'

        self._latex_repr = latex_repr

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join(srepr(var) for var in self._variables)

        if self._dimensions == PrintableGroup(*self._variables)._dimensions:
            dimensions_repr = ''
        else:
            dimensions_repr = f', dimensions={self._dimensions}'

        return f'{class_name}({variables_repr}{dimensions_repr})'

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return self._latex_repr


# Alias for DimensionalMatrix.
DimMatrix = DimensionalMatrix
