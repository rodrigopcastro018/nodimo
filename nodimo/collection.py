#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Collection
==========

This module contains the base class for everything that is created with
a collection of quantities.

Classes
-------
Collection
    Creates a collection of quantities.
"""

from sympy import sstr, latex, S, Number, Matrix, ImmutableDenseMatrix, eye
from sympy.printing.pretty.stringpict import prettyForm

from nodimo.dimension import Dimension
from nodimo.quantity import Quantity, Constant, One
from nodimo._internal import _show_object, _show_nodimo_warning


class Collection:
    """Collection of quantities.

    This is the base class for all classes created with a collection of
    quantities.

    Parameters
    ----------
    *quantities : Quantity
        Quantities that constitute the collection.

    Attributes
    ----------
    quantities : list[Quantity]
        List with the quantities that constitute the collection.

    Methods
    -------
    show(use_custom_css=True, use_unicode=True)
        Displays the collection in a pretty format.

    Raises
    ------
    TypeError
        If inputs to class are not instances of Quantity.
    ValueError
        If inputs contains different quantities with equal names.
    """

    def __init__(self, *quantities: Quantity):
        self._quantities: list[Quantity]
        self._dimensions: dict[str, Number]
        self._is_dimensionless: bool

        self._disassembled_quantities: list[Quantity]
        self._base_quantities: list[Quantity]

        self._number_constants: list[Constant]
        self._constants: list[Constant]

        self._scaling_quantities: list[Quantity]
        self._nonscaling_quantities: list[Quantity]

        self._dependent_quantities: list[Quantity]
        self._independent_quantities: list[Quantity]

        self._raw_matrix: list[list[Number]]
        self._matrix: ImmutableDenseMatrix
        self._rank: int
        self._rcef: ImmutableDenseMatrix
        self._independent_rows: tuple[int]
        self._submatrices: dict[Quantity, ImmutableDenseMatrix]

        self._set_collection_quantities(*quantities)
        self._set_collection()
        self._validate_collection()
        self._set_collection_dimensions()

    @property
    def quantities(self) -> list[Quantity]:
        return self._quantities

    def show(self, use_custom_css: bool = True, use_unicode: bool = True):
        _show_object(self, use_custom_css=use_custom_css, use_unicode=use_unicode)

    def _set_collection_quantities(self, *quantities: Quantity):
        not_quantities: list = []
        for qty in quantities:
            if not isinstance(qty, Quantity):
                not_quantities.append(qty)
        if len(not_quantities) > 0:
            raise TypeError(
                f"Non-quantity types given as input ({str(not_quantities)[1:-1]})"
            )

        self._quantities = list(quantities)

    def _set_collection(self):
        self._reduce_quantities()
        self._set_constants()
        self._set_disassembled_quantities()
        self._set_base_quantities()

    def _validate_collection(self):
        repeated_names = []
        for i, qty1 in enumerate(self._base_quantities):
            for qty2 in list(self._base_quantities)[i + 1 :]:
                repname = qty1.name if qty1.name == qty2.name else None
                if repname is not None and repname not in repeated_names:
                    repeated_names.append(repname)

        if len(repeated_names) > 0:
            raise ValueError(
                f"A collection can not contain different quantities "
                f"with equal names ({str(repeated_names)[1:-1]})"
            )

    def _set_collection_dimensions(self):
        """
        Dimensional exponents are set to NaN, unless all quantities
        share the same exponent for a particular dimension, case in
        which the exponent value is preserved.
        """

        dimensions = {}
        for qty in self._quantities:
            for dim in qty.dimension:
                if dim not in dimensions:
                    dimensions[dim] = S.NaN

        for dim in dimensions:
            same_dim = []
            for i, qty in enumerate(self._quantities):
                if dim not in qty.dimension:
                    same_dim.append(False)
                    break
                if i > 0:
                    same_dim.append(qty.dimension[dim] == qty_ref.dimension[dim])
                qty_ref = qty
            if all(same_dim):
                dimensions[dim] = qty_ref.dimension[dim]

        self._dimensions = dimensions
        self._is_dimensionless = all(dim == 0 for dim in dimensions.values())

    def _set_dimensions(self, **dimensions: Number):
        """Reserved for subclasses that need dimensions setting."""

        # Validate input dimensions in face of the collection's.
        dimension = Dimension(**dimensions)
        if not set(dimension).issubset(set(self._dimensions)):
            invalid_dimensions = []
            for dim in dimension:
                if dim not in self._dimensions:
                    invalid_dimensions.append(dim)
            raise ValueError(f"Invalid dimensions ({str(invalid_dimensions)[1:-1]})")

        for dim in self._dimensions:
            if dim not in dimension:
                dimension[dim] = S.Zero

        self._dimensions = dict(**dimension)
        self._set_matrix_independent_rows()
        self._is_dimensionless = all(dim == 0 for dim in self._dimensions.values())

    def _clear_null_dimensions(self):
        """Removes dimensions with null exponents."""

        dimensions = {}
        for dim, exp in self._dimensions.items():
            if exp != 0:
                dimensions[dim] = exp

        self._dimensions = dimensions

    def _clear_constants(self, only_numbers: bool = False, only_ones: bool = False):
        """Removes dimensionless constants.

        Parameters
        ----------
        only_numbers : bool, default=False
            If ``True``, only numerical constants are removed.
        only_ones : bool, default=False
            If ``True``, only instances of One are removed.
        """

        if only_numbers:
            constants = self._number_constants
        elif only_ones:
            constants = [One()]
        else:
            constants = self._constants

        clear_quantities = []
        for qty in self._quantities:
            if qty not in constants:
                clear_quantities.append(qty)

        self._quantities = clear_quantities
        self._set_collection()

    def _reduce_quantities(self):
        self._quantities = list(qty.reduce() for qty in self._quantities)

    def _set_disassembled_quantities(self):
        """Determines all instances of Quantity, Constant and Power.

        It does that by disassembling instances of Product.
        """

        disassembled_quantities = []
        for qty in self._quantities:
            if qty._is_product:
                disassembled_quantities.extend(qty.factors)
            else:
                disassembled_quantities.append(qty)

        self._disassembled_quantities = list(disassembled_quantities)

    def _set_base_quantities(self):
        """Determines all nonnumerical instances of Quantity."""

        base_quantities = []
        for qty in self._disassembled_quantities:
            if qty._is_power:
                base_qty = qty.base
            else:
                base_qty = qty

            if not base_qty._symbolic.is_number and base_qty not in base_quantities:
                base_quantities.append(base_qty)

        self._base_quantities = list(base_quantities)

    def _set_constants(self):
        """Determines all nonrepetitive instances of Constant."""

        number_constants = []
        constants = []
        for qty in self._quantities:
            if qty._is_constant and qty not in constants:
                if qty._is_number:
                    number_constants.append(qty)
                constants.append(qty)

        self._number_constants = list(number_constants)
        self._constants = list(constants)

    def _set_scaling_quantities(self):
        """Separates scaling and nonscaling quantities."""

        scaling_quantities = []
        nonscaling_quantities = []
        for qty in self._quantities:
            if qty.is_scaling:
                scaling_quantities.append(qty)
            else:
                nonscaling_quantities.append(qty)

        self._scaling_quantities = list(scaling_quantities)
        self._nonscaling_quantities = list(nonscaling_quantities)

    def _set_dependent_quantities(self):
        """Separates dependent and independent quantities."""

        dependent_quantities = []
        independent_quantities = []
        for qty in self.quantities:
            if qty.is_dependent:
                dependent_quantities.append(qty)
            else:
                independent_quantities.append(qty)

        self._dependent_quantities = list(dependent_quantities)
        self._independent_quantities = list(independent_quantities)

    def _set_matrix(self):
        """Builds basic dimensional matrix."""

        raw_matrix = []
        for dim in self._dimensions:
            dim_exponents = []
            for qty in self._quantities:
                if dim in qty.dimension:
                    dim_exponents.append(qty.dimension[dim])
                else:
                    dim_exponents.append(S.Zero)
            raw_matrix.append(dim_exponents)

        self._raw_matrix = raw_matrix
        self._matrix = ImmutableDenseMatrix(raw_matrix)

    def _set_matrix_rank(self):
        if not hasattr(self, '_matrix'):
            self._set_matrix()

        self._rank = self._matrix.rank()

    def _set_matrix_independent_rows(self):
        """Independent rows are also independent dimensions.

        This method also takes the opportunity to fix dimensions set by
        the user, specially when the dimensions are not all independent.
        """

        if not hasattr(self, '_rank'):
            self._set_matrix_rank()

        if len(self._dimensions) > self._rank and len(self._quantities) > self._rank:
            # In case the number of dimensions is larger than the rank,
            # the dimensions are not all independent.
            rref, independent_rows = self._matrix.T.rref()
            rcef = rref.T[:, : len(self._dimensions)]
            exponents = rcef @ Matrix(list(self._dimensions.values()))
            dimensions = dict(zip(self._dimensions, exponents[:]))
            independent_dimensions = {}
            for i, dim in enumerate(self._dimensions):
                if i in independent_rows:
                    independent_dimensions[dim] = self._dimensions[dim]

            dimensions_str = ', '.join(dim for dim in self._dimensions)
            indep_dimensions_str = ', '.join(dim for dim in independent_dimensions)
            _show_nodimo_warning(
                f"From the dimensions ({dimensions_str}), only "
                f"({indep_dimensions_str}) are treated as independent"
            )
        else:
            rcef = eye(len(self._dimensions))
            independent_rows = tuple(range(len(self._dimensions)))
            dimensions = self._dimensions
            independent_dimensions = self._dimensions.copy()

        self._rcef = rcef
        self._independent_rows = independent_rows
        self._dimensions = dimensions
        self._independent_dimensions = independent_dimensions

    def _set_submatrices(self):
        """Builds one column matrix for each quantity."""

        if not hasattr(self, '_matrix'):
            self._set_matrix()

        submatrices = []
        for i, qty in enumerate(self._quantities):
            submatrices.append((qty, self._matrix.col(i)))

        self._submatrices = dict(submatrices)

    def _get_submatrix(self, *quantities) -> ImmutableDenseMatrix:
        """Combines the quantities' submatrices into one submatrix.

        Parameters
        ----------
        *quantities : Quantity
            Quantities used to build the submatrix.

        Returns
        -------
        submatrix : Matrix
            The submatrix built from the given quantities.

        Raises
        ------
        ValueError
            If the given quantities are not all part of the collection.
        """

        if not set(quantities).issubset(set(self._quantities)):
            raise ValueError(f"'{quantities}' is not a subset of '{self._quantities}'")
        elif not hasattr(self, '_submatrices'):
            self._set_submatrices()

        submatrices = [self._submatrices[qty] for qty in quantities]
        submatrix = ImmutableDenseMatrix.hstack(*submatrices)

        return submatrix

    def _key(self) -> tuple:
        return (frozenset(self._quantities),)

    def __hash__(self) -> int:
        return hash(self._key())

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        elif isinstance(other, type(self)):
            return self._key() == other._key()
        return False

    def __contains__(self, item) -> bool:
        return self._quantities.__contains__(item)

    def __len__(self) -> int:
        return self._quantities.__len__()

    def __iter__(self):
        return self._quantities.__iter__()

    def __next__(self):
        return self.__iter__().__next__()

    def __str__(self) -> str:
        return sstr(self)

    __repr__ = __str__

    def __getitem__(self, indexes):
        return self._quantities[indexes]

    def _repr_latex_(self):
        """Latex representation according to IPython/Jupyter."""

        return f'$\\displaystyle {latex(self)}$'

    def _sympy_(self):
        from sympy import sympify

        return sympify(self._quantities)

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        quantities = ', '.join(
            printer._print(qty._unreduced) for qty in self._quantities
        )

        return f'{class_name}({quantities})'

    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy."""

        class_name = printer._print(type(self).__name__)
        quantities = ', '.join(
            printer._print(qty._unreduced) for qty in self._quantities
        )

        return f'{class_name}({quantities})'

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        class_name = printer._print(type(self).__name__)
        quantities = R',\ '.join(
            printer._print(qty._unreduced) for qty in self._quantities
        )

        return f'{class_name}\\left({quantities}\\right)'

    def _pretty(self, printer) -> prettyForm:
        """Pretty representation according to Sympy."""

        class_name = printer._print(type(self).__name__)

        quantities = prettyForm('')
        for i, qty in enumerate(self._quantities):
            sep = ', ' if i > 0 else ''
            quantities = prettyForm(
                *quantities.right(sep, printer._print(qty._unreduced))
            )
        quantities = prettyForm(*quantities.parens())

        return prettyForm(*class_name.right(quantities))
