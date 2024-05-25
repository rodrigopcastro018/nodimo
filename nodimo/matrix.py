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

from sympy import Symbol, ImmutableDenseMatrix, Matrix

from nodimo.variable import Variable
from nodimo.groups import Group


class DimensionalMatrix(Group):
    """Creates a dimensional matrix from a group of variables.

    Similar to a BasicDimensionalMatrix, but with labels at the side and
    at the top of the matrix to display the dimensions and variables.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the dimensional matrix.

    Attributes
    ----------
    variables : tuple[Variable]
        List with the variables used to build the dimensional matrix.
    matrix : ImmutableDenseMatrix
        Dimensional matrix containing only the dimensions' exponents.
    rank : int
        The rank of the dimensional matrix.
    independent_rows : tuple[int]
        Indexes of the dimensional matrix independent rows.

    Methods
    -------
    set_dimensions_order(*dimensions_names)
        Sets the dimensions column order.
    show()
        Displays the labeled dimensional matrix.

    Examples
    --------
    >>> from nodimo import Variable, DimensionalMatrix
    >>> F = Variable('F', M=1, L=1, T=-2)
    >>> k = Variable('m', M=1, T=-2)
    >>> x = Variable('a', L=1)
    >>> dmatrix = DimensionalMatrix(F, k, x)
    >>> dmatrix.show()
    """

    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._set_dimensional_matrix()

    @property
    def matrix(self) -> ImmutableDenseMatrix:
        return self._matrix

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def independent_rows(self) -> tuple[int]:
        return self._independent_rows

    def _set_dimensional_matrix(self):
        self._set_matrix()
        self._set_matrix_rank()
        self._set_matrix_independent_rows()
        self._set_symbolic_dimensional_matrix()

    def _set_symbolic_dimensional_matrix(self):
        labeled_matrix = self._matrix.as_mutable()
        dimensions_matrix = Matrix(list(self._dimensions))
        variables_matrix = Matrix([[Symbol('')] + list(self._variables)])
        labeled_matrix = labeled_matrix.col_insert(0, dimensions_matrix)
        labeled_matrix = labeled_matrix.row_insert(0, variables_matrix)

        self._symbolic = labeled_matrix.as_immutable()

    def _sympy_(self):
        return self._matrix

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variables = ', '.join(printer._print(var) for var in self._variables)

        return f'{class_name}({variables})'

    def _sympystr(self, printer) -> str:
        return self._symbolic.table(printer, rowstart='', rowend='', colsep='  ')

    def _latex(self, printer) -> str:
        dmatrix = R'\begin{array}'
        dmatrix += '{r|' + 'r' * len(self._variables) + '} & '
        dmatrix += ' & '.join([printer._print(var) for var in self._variables])
        dmatrix += R'\\ \hline '
        for dim, exponents in zip(self._dimensions, self._raw_matrix):
            row = [printer._print(dim)]
            for exp in exponents:
                if exp < 0:
                    row.append(printer._print(exp))
                else:
                    # Mimic the minus sign to preserve column width.
                    row.append(R'\phantom{-}' + printer._print(exp))
            dmatrix += ' & '.join(row) + R'\\'
        dmatrix += R'\end{array}'

        return dmatrix

    def _pretty(self, printer):
        return printer._print_matrix_contents(self._symbolic)

    def set_dimensions_order(self, *dimensions_names: str):
        """Sets the dimensions column order.

        Parameters
        ----------
        *dimensions_names : str
            Dimensions' names in the requested order.
        """

        dimensions = dict((dim, 0) for dim in dimensions_names)
        for dim in self._dimensions:
                dimensions[dim] = self._dimensions[dim]

        self._set_dimensions(**dimensions)
        self._set_dimensional_matrix()


# Alias for DimensionalMatrix.
DimMatrix = DimensionalMatrix
