#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Matrix
======

This module contains the class to create a dimensional matrix.

Classes
-------
DimensionalMatrix
    Creates a dimensional matrix from a group of quantities.
"""

from sympy import Symbol, ImmutableDenseMatrix, Matrix

from nodimo.quantity import Quantity
from nodimo.groups import Group


class DimensionalMatrix(Group):
    """Dimensional matrix of a group of quantities.

    A DimensionalMatrix is a matrix with one column for each quantity,
    one row for each dimension's name, and every element represents the
    dimension's exponent of a particular quantity. Labels at the top
    and at the right side are added to identify the quantities and the
    dimensions' names, respectively.

    Parameters
    ----------
    *quantities : Quantity
        Quantities that constitute the dimensional matrix.

    Attributes
    ----------
    quantities : tuple[Quantity]
        List with the quantities used to build the dimensional matrix.
    matrix : ImmutableDenseMatrix
        Dimensional matrix containing only the dimensions' exponents.
    rank : int
        The rank of the dimensional matrix.
    independent_rows : tuple[int]
        Indexes of the dimensional matrix independent rows.

    Methods
    -------
    set_dimensions_order(*dimensions_names)
        Sets the dimensions' names order.
    show()
        Displays the dimensional matrix.

    Examples
    --------

    >>> from nodimo import Quantity, Product, DimensionalMatrix
    >>> F = Quantity('F', M=1, L=1, T=-2)
    >>> k = Quantity('m', M=1, T=-2)
    >>> x = Quantity('a', L=1)
    >>> kx = Product(k, x)
    >>> dmatrix = DimensionalMatrix(F, k, x, kx)
    >>> dmatrix.show()
    """

    def __init__(self, *quantities: Quantity):
        super().__init__(*quantities)
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
        dimensions_column = Matrix(list(self._dimensions))
        quantities_row = Matrix([[Symbol('')] + list(self._quantities)])
        labeled_matrix = labeled_matrix.col_insert(0, dimensions_column)
        labeled_matrix = labeled_matrix.row_insert(0, quantities_row)

        self._symbolic = labeled_matrix.as_immutable()

    def _sympy_(self):
        return self._matrix

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantities = ', '.join(printer._print(qty) for qty in self._quantities)

        return f'{class_name}({quantities})'

    def _sympystr(self, printer) -> str:
        return self._symbolic.table(printer, rowstart='', rowend='', colsep='  ')

    def _latex(self, printer) -> str:
        dmatrix = R'\begin{array}'
        dmatrix += '{r|' + 'r' * len(self._quantities) + '} & '
        dmatrix += ' & '.join([printer._print(qty) for qty in self._quantities])
        dmatrix += R' \\ \hline '
        for dim, exponents in zip(self._dimensions, self._raw_matrix):
            row = [f'\\mathsf{{{dim}}}']
            for exp in exponents:
                if exp < 0:
                    row.append(printer._print(exp))
                else:
                    # Mimic the minus sign to preserve column width.
                    row.append(R'\phantom{-}' + printer._print(exp))
            dmatrix += ' & '.join(row) + R' \\ '
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
