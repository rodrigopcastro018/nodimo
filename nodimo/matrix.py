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

from sympy import Symbol, ImmutableDenseMatrix, Matrix, S
from sympy.printing.pretty.stringpict import prettyForm

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
    quantities : list[Quantity]
        List with the quantities used to build the dimensional matrix.
    matrix : ImmutableDenseMatrix
        Matrix containing only the dimensions' exponents.
    rank : int
        The rank of the dimensional matrix.
    independent_rows : tuple[int]
        Indexes of the dimensional matrix independent rows.

    Methods
    -------
    set_dimensions_order(*dimensions_names)
        Sets the dimensions' names order.
    show(use_custom_css=True, use_unicode=True)
        Displays the dimensional matrix.

    Warns
    -----
    NodimoWarning
        Dimensions that are treated as independent.

    Examples
    --------

    >>> from nodimo import Quantity, DimensionalMatrix
    >>> F = Quantity('F', M=1, L=1, T=-2)
    >>> k = Quantity('k', M=1, T=-2)
    >>> x = Quantity('x', L=1)
    >>> dmatrix = DimensionalMatrix(F, k, x, k*x)
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

    def set_dimensions_order(self, *dimensions_names: str):
        """Sets the dimensions column order.

        Parameters
        ----------
        *dimensions_names : str
            Dimensions' names in the requested order.
        """

        dimensions = dict((dim, S.Zero) for dim in dimensions_names)
        for dim in self._dimensions:
            dimensions[dim] = self._dimensions[dim]

        self._set_dimensions(**dimensions)
        self._set_matrix()
        self._set_symbolic_dimensional_matrix()

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
        nrows = len(self._dimensions) + 1
        ncols = len(self._quantities) + 1
        raw_dmatrix = {}
        for i in range(nrows):
            for j in range(ncols):
                if i == j == 0:
                    raw_dmatrix[i, j] = printer._print('')
                elif i == 0:
                    raw_dmatrix[i, j] = printer._print(self._quantities[j - 1])
                elif j == 0:
                    raw_dmatrix[i, j] = printer._print(list(self._dimensions)[i - 1])
                else:
                    raw_dmatrix[i, j] = printer._print(self._matrix[i - 1, j - 1])

        maxwidth = []
        for j in range(ncols):
            maxwidth.append(max(len(raw_dmatrix[i, j]) for i in range(nrows)))

        for i in range(nrows):
            for j in range(ncols):
                nspaces = maxwidth[j] - len(raw_dmatrix[i, j])
                left_space = ' ' * nspaces
                raw_dmatrix[i, j] = left_space + raw_dmatrix[i, j]

        rows = []
        for i in range(nrows):
            row = '  '.join(raw_dmatrix[i, j] for j in range(ncols))
            rows.append(row)
        dmatrix = '\n'.join(rows)

        return dmatrix

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

    def _pretty(self, printer) -> prettyForm:
        nrows = len(self._dimensions) + 1
        ncols = len(self._quantities) + 1
        raw_dmatrix = {}
        for i in range(nrows):
            for j in range(ncols):
                if i == j == 0:
                    raw_dmatrix[i, j] = printer._print('')
                elif i == 0:
                    raw_dmatrix[i, j] = printer._print(self._quantities[j - 1])
                elif j == 0:
                    raw_dmatrix[i, j] = printer._print(list(self._dimensions)[i - 1])
                else:
                    raw_dmatrix[i, j] = printer._print(self._matrix[i - 1, j - 1])

        maxwidth = []
        for j in range(ncols):
            maxwidth.append(max(raw_dmatrix[i, j].width() for i in range(nrows)))

        for i in range(nrows):
            for j in range(ncols):
                nspaces = 0 if j == 0 else 2
                nspaces += maxwidth[j] - raw_dmatrix[i, j].width()
                left_space = prettyForm(' ' * nspaces)
                raw_dmatrix[i, j] = prettyForm(*left_space.right(raw_dmatrix[i, j]))

        for i in range(nrows):
            row = raw_dmatrix[i, 0]
            for j in range(1, ncols):
                row = prettyForm(*row.right(raw_dmatrix[i, j]))

            if i == 0:
                dmatrix = row
            else:
                dmatrix = prettyForm(*dmatrix.below(row))

        return dmatrix
