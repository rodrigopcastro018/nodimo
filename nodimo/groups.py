#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Groups
======

This module contains classes to create groups of quantities, which are
specific types of collections.

Classes
-------
Group
    Creates a group of quantities.
HomogeneorusGroup
    Creates a homogeneous group of quantities.
ScalingGroup
    Creates a Group of scaling quantities.
PrimeGroup
    Creates a group of prime quantities.
DimensionalGroup
    Creates a dimensional group of derived quantities.
"""

from sympy import Number, Matrix, zeros, eye
from sympy.printing.pretty.stringpict import prettyForm

from nodimo.quantity import Quantity
from nodimo.collection import Collection
from nodimo.power import Power
from nodimo.product import Product
from nodimo._internal import _unsympify_number, _show_nodimo_warning


class Group(Collection):
    """Group of quantities.

    Equivalent to a Collection, but duplicate quantities are removed.

    Warns
    -----
        Removed duplicate quantities.
    """

    def __init__(self, *quantities: Quantity):
        super().__init__(*quantities)
        self._set_group()

    def _set_group(self):
        self._clear_duplicate_quantities()

    def _clear_duplicate_quantities(self):
        duplicate_quantities = []
        clear_quantities = []
        for qty in self._quantities:
            if qty not in clear_quantities:
                clear_quantities.append(qty)
            else:
                duplicate_quantities.append(qty)

        self._quantities = tuple(clear_quantities)

        if len(duplicate_quantities) > 0:
            _show_nodimo_warning(
                f"Duplicate quantities ({str(duplicate_quantities)[1:-1]})"
            )


class HomogeneousGroup(Group):
    """Dimensionally homogeneous group of quantities.

    Equivalent to a dimmensionally homogenous Group.

    Warns
    -----
    NodimoWarning
        Removed dimensionally irrelevant quantities.
    """

    def __init__(self, *quantities: Quantity):
        super().__init__(*quantities)
        self._set_homogeneous_group()

    def _set_homogeneous_group(self):
        self._clear_heterogeneous_quantities()

    def _clear_heterogeneous_quantities(self):
        clear_quantities = list(self._quantities)
        irrelevant_quantities = []
        for _ in self._quantities:
            irr_qty = None
            for dim in self._dimensions:
                dim_bool = []
                for qty in clear_quantities:
                    if dim in qty.dimension:
                        dim_bool.append(True)
                    else:
                        dim_bool.append(False)

                dim_count = sum(dim_bool)
                if dim_count == 1:
                    irr_qty = clear_quantities[dim_bool.index(True)]
                    irrelevant_quantities.append(irr_qty)
                    clear_quantities.remove(irr_qty)
                    self._quantities = tuple(clear_quantities)
                    self._set_collection_dimensions()
                    break
            if irr_qty is None:
                break

        if len(irrelevant_quantities) > 0:
            _show_nodimo_warning(f"Dimensionally irrelevant quantities "
                                 f"({str(irrelevant_quantities)[1:-1]})")


class ScalingGroup(Group):
    """A Group of scaling quantities.

    Raises
    ------
    ValueError
        If the quantities are not dimensionally independent.
    """

    def __init__(self, *quantities: Quantity, id_number: int = 0):
        super().__init__(*quantities)
        self._id_number: int = id_number
        self._set_scaling_group()

    def _set_scaling_group(self):
        self._clear_ones()
        self._set_scaling_group_quantities()
        self._set_matrix_rank()
        self._validate_scaling_group()

    def _set_scaling_group_quantities(self):
        """Sets all quantities in the group as scaling."""

        new_quantities = []
        for qty in self._quantities:
            if qty.is_scaling:
                new_qty = qty
            else:
                new_qty = qty._copy()
                new_qty.is_scaling = True
            new_quantities.append(new_qty)

        self._quantities = tuple(new_quantities)

    def _validate_scaling_group(self):
        if len(self._quantities) != self._rank:
            raise ValueError("Quantities are not dimensionally independent")

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantities = ', '.join(printer._print(qty) for qty in self._quantities)
        id_number = f', id_number={self._id_number}' if self._id_number else ''

        return f'{class_name}({quantities}{id_number})'

    def _sympystr(self, printer) -> str:
        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")
        quantities = ', '.join(printer._print(qty) for qty in self._quantities)

        return f'{scgroup}({quantities})'

    def _latex(self, printer) -> str:
        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")
        quantities = R',\ '.join(printer._print(qty) for qty in self._quantities)

        return f'{scgroup}\\left({quantities}\\right)'

    def _pretty(self, printer) -> prettyForm:
        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")

        quantities = prettyForm('')
        for i, qty in enumerate(self._quantities):
            sep = ', ' if i > 0 else ''
            quantities = prettyForm(*quantities.right(sep, printer._print(qty)))
        quantities = prettyForm(*quantities.parens())

        return prettyForm(*scgroup.right(quantities))


class IndependentGroup(Group):
    """Independent group of quantities.

    A group is independent if any quantity in it cannot be obtained as
    the product of powers of the other quantities of the group.

    In the context of this class, all quantities are considered derived,
    that is, all quantities are expressed as products of powers of the
    base quantities of the group. This allow us to remove derived
    quantities that are dependent on other derived quantities.

    To find dependent derived quantities, they are defined in such a way
    that their dimensions use the names of the base quantities as the
    dimensions' names and the exponents of the base quantities as the
    dimensions' exponents. The resulting dimensional matrix and its rank
    will determine the independency status of the group.

    Warns
    -----
    NodimoWarning
        Removed dependent derived quantities.

    Notes
    -----
    1. The terms 'dependent' and 'independent' have nothing to do with
       the quantity attribute (is_dependent) used to build relations.
    2. The base quantities are not necessarily the quantities of the
       group.
    """

    def __init__(self, *quantities: Quantity):
        super().__init__(*quantities)
        self._derived_quantities: tuple[Quantity]
        self._set_independent_group()

    def _set_independent_group(self):
        self._clear_ones()
        self._set_derived_quantities()
        self._clear_dependent_derived_quantities()

    def _get_derived_dimensions(self, quantity) -> dict[str, Number]:
        dimensions = {}
        if quantity._is_product:
            for qty in quantity.quantities:
                dimensions = {**dimensions, **self._get_derived_dimensions(qty)}
        elif quantity._is_power:
            dimensions[quantity.quantity.name] = quantity.exponent
        else:
            dimensions[quantity.name] = 1

        return dimensions

    def _set_derived_quantities(self):
        derived_quantities = []
        for i, qty in enumerate(self._quantities):
            dimensions = self._get_derived_dimensions(qty)
            derived_quantities.append(Quantity(f'b_{i}', **dimensions))

        self._derived_quantities = tuple(derived_quantities)

    def _clear_dependent_derived_quantities(self):
        derived_group = Group(*self._derived_quantities)
        derived_group._set_matrix_rank()
        if len(self._derived_quantities) > derived_group._rank:
            _, indep_qts_indexes = derived_group._matrix.rref()
        else:
            indep_qts_indexes = tuple(range(len(self._derived_quantities)))

        independent_quantities = []
        dependent_quantities = []
        for i, qty in enumerate(self._quantities):
            if i in indep_qts_indexes:
                independent_quantities.append(qty)
            else:
                dependent_quantities.append(qty)

        self._quantities = tuple(independent_quantities)

        if len(dependent_quantities) > 0:
            _show_nodimo_warning(
                f"Dependent derived quantities ({str(dependent_quantities)[1:-1]})"
            )


class DimensionalGroup(HomogeneousGroup, IndependentGroup):
    """Dimensional group of derived quantities.

    This class creates a group of derived quantities from a homogeneous
    and independent group of provided quantities. The derived quantities
    are built as products of powers of the original quantities in a way
    that all derived quantities contain the same requested dimension.

    To achieve this, one must provide quantities with scaling property,
    in a number that matches the rank of the original group. The scaling
    quantities work as tranformation parameters that, combined with the
    nonscaling quantities, produce derived quantities with the demanded
    dimension. The ensuing number of derived quantities is always lower
    or equal to the number of original quantities.

    Parameters
    ----------
    *quantities : Quantity
        Quantities to be transformed.
    **dimensions : Number
        Aimed dimensions for the group given as keyword arguments.
        Dimensions that are given are considered null.

    Raises
    ------
    ValueError
        If the group does not have the necessary number of dimensionally
        independent scaling quantities.

    References
    ----------
    .. [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
           (Butterworth-Heinemann, 2007), p. 133.
    """

    def __init__(self, *quantities: Quantity, **dimensions: Number):
        super(DimensionalGroup, self).__init__(*quantities)
        super(HomogeneousGroup, self).__init__(*self._quantities)
        self._xquantities: tuple[Quantity] = self._quantities
        self._set_dimensions(**dimensions)
        self._set_dimensional_group()

    def _set_dimensional_group(self):
        self._set_scaling_quantities()
        self._set_scaling_matrix()
        self._validate_dimensional_group()
        self._set_exponents()
        self._set_dimensional_group_quantities()
        self._clear_duplicate_quantities()
        self._clear_null_dimensions()

    def _set_scaling_matrix(self):
        scaling_matrix = self._get_submatrix(*self._scaling_quantities)
        nonscaling_matrix = self._get_submatrix(*self._nonscaling_quantities)

        self._scaling_matrix = scaling_matrix[self._independent_rows, :]
        self._nonscaling_matrix = nonscaling_matrix[self._independent_rows, :]

    def _validate_dimensional_group(self):
        check1 = len(self._scaling_quantities) == self._rank
        check2 = self._scaling_matrix.rank() == self._rank
        if not check1 or not check2:
            raise ValueError(
                f"The group must have {self._rank} "
                f"dimensionally independent scaling quantities"
            )

    def _set_exponents(self):
        """Sets the exponents to build the products of powers."""

        nqts = len(self._quantities)
        rank = self._rank
        hasdim = int(not self._is_dimensionless)
        nnonsc = nqts - rank
        nprods = nnonsc + hasdim

        A = self._scaling_matrix
        B = self._nonscaling_matrix

        E11 = eye(nnonsc)
        E12 = zeros(nnonsc, rank)
        E21 = -A**-1 * B
        E22 = A**-1
        E = Matrix([[E11, E12],
                    [E21, E22]])

        Z1 = Matrix.hstack(eye(nnonsc), zeros(nnonsc, hasdim))
        Z2C = Matrix(list(self._independent_dimensions.values()))
        Z2 = Matrix.hstack(*nprods*[Z2C])
        Z = Matrix([[Z1],
                    [Z2]])

        P = E * Z

        self._exponents = P.as_immutable()

    def _set_dimensional_group_quantities(self):
        quantities = self._nonscaling_quantities + self._scaling_quantities
        products = []
        for j in range(self._exponents.cols):
            factors = []
            for qty, exp in zip(quantities, self._exponents.col(j)):
                factors.append(Power(qty, exp))
            products.append(Product(*factors))

        self._quantities = tuple(products)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantities = ', '.join(printer._print(qty) for qty in self._xquantities)

        if self._is_dimensionless:
            dimensions = ''
        else:
            dims = []
            for dim_name, dim_exp in self._dimensions.items():
                dim_exp_ = _unsympify_number(dim_exp)
                if isinstance(dim_exp_, str):
                    dim_exp_ = f"'{dim_exp_}'"
                dims.append(f'{dim_name}={dim_exp_}')
            dimensions = f", {', '.join(dims)}"

        return f'{class_name}({quantities}{dimensions})'
