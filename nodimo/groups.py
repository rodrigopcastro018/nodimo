#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Groups
======

This module contains classes to create groups of variables, which are
specific types of collections.

Classes
-------
Group
    Creates a group of variables.
HomogeneorusGroup
    Creates a homogeneous group of variables.
ScalingGroup
    Creates a Group of scaling variables.
PrimeGroup
    Creates a group of prime variables.
DimensionalGroup
    Creates a (non)dimensional group of variables.
"""

from sympy import Matrix, zeros, eye
from sympy.printing.pretty.stringpict import prettyForm
from typing import Optional

from nodimo.variable import Variable
from nodimo.collection import Collection
from nodimo.power import Power
from nodimo.product import Product
from nodimo._internal import _unsympify_number, _show_nodimo_warning


class Group(Collection):  # What if my input contains two equal variables, but one of them is dependent.
    """Group of variables.

    Equivalent to a Collection, but duplicate variables are removed.

    Warns
    -----
        Removed duplicate variables.
    """

    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._set_group()

    def _set_group(self):
        self._clear_duplicate_variables()

    def _clear_duplicate_variables(self):
        duplicate_variables = []
        clear_variables = []
        for var in self._variables:
            if var not in clear_variables:
                clear_variables.append(var)
            else:
                duplicate_variables.append(var)

        self._variables = tuple(clear_variables)

        if len(duplicate_variables) > 0:
            _show_nodimo_warning(
                f"Removed duplicate variables ({str(duplicate_variables)[1:-1]})"
            )


class HomogeneousGroup(Group):
    """Dimensionally homogeneous group of variables.

    Equivalent to a dimmensionally homogenous Group.

    Warns
    -----
    NodimoWarning
        Removed dimensionally heterogeneous variables.
    """

    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._set_homogeneous_group()

    def _set_homogeneous_group(self):
        self._clear_heterogeneous_variables()

    def _clear_heterogeneous_variables(self):
        clear_variables = list(self._variables)
        heterogeneous_variables = []
        for _ in self._variables:
            htg_var = None
            for dim in self._dimensions:
                dim_bool = []
                for var in clear_variables:
                    if dim in var.dimensions:
                        dim_bool.append(True)
                    else:
                        dim_bool.append(False)

                dim_count = sum(dim_bool)
                if dim_count == 1:
                    htg_var = clear_variables[dim_bool.index(True)]
                    heterogeneous_variables.append(htg_var)
                    clear_variables.remove(htg_var)
                    self._variables = tuple(clear_variables)
                    self._set_collection_dimensions()
                    break
            if htg_var is None:
                break

        if len(heterogeneous_variables) > 0:
            _show_nodimo_warning(f"Removed dimensionally heterogeneous variables "
                                 f"({str(heterogeneous_variables)[1:-1]})")


class ScalingGroup(Group):
    """A Group of scaling variables.

    Raises
    ------
    ValueError
        If the variables are not dimensionally independent.
    """

    def __init__(self, *variables: Variable, id_number: Optional[int] = None):
        super().__init__(*variables)
        self._id_number: int = id_number
        self._set_scaling_group()

    def _set_scaling_group(self):
        self._clear_ones()
        self._set_scaling_group_variables()
        self._set_matrix_rank()
        self._validate_scaling_group()

    def _set_scaling_group_variables(self):
        """Sets all variables in the group as scaling."""

        new_variables = []
        for var in self._variables:
            if var.is_scaling:
                new_var = var
            else:
                new_var = var._copy()
                new_var.is_scaling = True
            new_variables.append(new_var)

        self._variables = tuple(new_variables)

    def _validate_scaling_group(self):
        if len(self._variables) != self._rank:
            raise ValueError("Variables are not dimensionally independent")

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variables = ', '.join(printer._print(var) for var in self._variables)
        id_number = f', id_number={self._id_number}' if self._id_number else ''

        return f'{class_name}({variables}{id_number})'

    def _sympystr(self, printer) -> str:
        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")
        variables = ', '.join(printer._print(var) for var in self._variables)

        return f'{scgroup}({variables})'

    def _latex(self, printer) -> str:
        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")
        variables = R',\ '.join(printer._print(var) for var in self._variables)

        return f'{scgroup}\\left({variables}\\right)'

    def _pretty(self, printer) -> prettyForm:
        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")

        variables = prettyForm('')
        for i, var in enumerate(self._variables):
            sep = ', ' if i > 0 else ''
            variables = prettyForm(*variables.right(sep, printer._print(var)))
        variables = prettyForm(*variables.parens())

        return prettyForm(*scgroup.right(variables))


class PrimeGroup(Group):
    """Group of prime variables.

    A variable is prime if it can not be obtained as the product of
    powers of the other variables of the group.

    Warns
    -----
    NodimoWarning
        Removed nonprime variables.

    Notes
    -----
    The process used to create this group is similar to what is done in
    ScalingGroup and DimensionalGroup. The trick consists of creating a
    new group of variables (bariables), which use base variables' names
    as dimensions.
    """

    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._bariables: tuple[Variable]
        self._set_independent_group()

    def _set_independent_group(self):
        self._clear_ones()
        self._set_bariables()
        self._clear_nonprime_variables()

    def _get_bariable_dimensions(self, variable):
        dimensions = {}
        if variable._is_product:
            for var in variable.variables:
                bardims = self._get_bariable_dimensions(var)
                dimensions = {**dimensions, **bardims}
        elif variable._is_power:
            dim = variable.variable.name
            dimensions[dim] = variable.exponent
        elif variable._is_variable:
            dim = variable.name
            dimensions[dim] = 1

        return dimensions
    
    def _set_bariables(self):
        bariables = []
        for i, var in enumerate(self._variables):
            bardims = self._get_bariable_dimensions(var)
            bariables.append(Variable(f'b_{i}', **bardims))

        self._bariables = tuple(bariables)

    def _clear_nonprime_variables(self):
        bargroup = Group(*self._bariables)
        bargroup._set_matrix_rank()
        if len(self._bariables) > bargroup._rank:
            _, prime_bariables = bargroup._matrix.rref()
        else:
            prime_bariables = tuple(range(len(self._bariables)))

        prime_variables = []
        nonprime_variables = []
        for i, var in enumerate(self._variables):
            if i in prime_bariables:
                prime_variables.append(var)
            else:
                nonprime_variables.append(var)

        self._variables = tuple(prime_variables)

        if len(nonprime_variables) > 0:
            _show_nodimo_warning(
                f"Removed nonprime variables ({str(nonprime_variables)[1:-1]})"  # TODO: derived quantities
            )


class DimensionalGroup(HomogeneousGroup, PrimeGroup):
    """Transformed (non)dimensional group of variables.

    This class creates a new group of variables from a homogeneous given
    group of variables. The resulting group has all variables with the
    same dimension.

    Parameters
    ----------
    *variables : Variable
        Variables to be transformed.
    **dimensions : int
        Aimed dimensions for the group given as keyword arguments.

    Raises
    ------
    ValueError
        If the group does not have the necessary number of dimensionally
        independent scaling variables.
    """

    def __init__(self, *variables: Variable, **dimensions: int):
        super(DimensionalGroup, self).__init__(*variables)
        super(HomogeneousGroup, self).__init__(*self._variables)
        self._is_nondimensional: bool
        self._xvariables: tuple[Variable] = self._variables
        self._set_dimensions(**dimensions)
        self._set_dimensional_group()

    def _set_dimensional_group(self):
        self._set_scaling_variables()
        self._set_matrix_independent_rows()
        self._set_scaling_matrix()
        self._validate_dimensional_group()
        self._set_exponent_matrix()
        self._set_dimensional_group_variables()
        self._clear_null_dimensions()

    def _set_scaling_matrix(self):
        scaling_matrix = self._get_submatrix(*self._scaling_variables)
        nonscaling_matrix = self._get_submatrix(*self._nonscaling_variables)

        self._scaling_matrix = scaling_matrix[self._independent_rows, :]
        self._nonscaling_matrix = nonscaling_matrix[self._independent_rows, :]

    def _validate_dimensional_group(self):
        check1 = len(self._scaling_variables) == self._rank
        check2 = self._scaling_matrix.rank() == self._rank
        if not check1 or not check2:
            raise ValueError(
                f"The group must have {self._rank} "
                f"dimensionally independent scaling variables"
            )

    def _set_exponent_matrix(self):
        """Determines the exponent of each variable, for every product.

        References
        ----------
        .. [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
               (Butterworth-Heinemann, 2007), p. 133.
        """

        nvars = len(self._variables)
        rank = self._rank
        nprods = nvars - rank

        A = self._scaling_matrix
        B = self._nonscaling_matrix

        E11 = eye(nprods)
        E12 = zeros(nprods, rank)
        E21 = -A**-1 * B
        E22 = A**-1
        E = Matrix([[E11, E12],
                    [E21, E22]])

        Z1 = eye(nprods)
        Z2C = Matrix(list(self._dimensions.values()))
        Z2 = Matrix.hstack(*nprods*[Z2C])
        Z = Matrix([[Z1],
                    [Z2]])

        exponents = E * Z

        self._exponents = exponents.as_immutable()

    def _set_dimensional_group_variables(self):
        variables = self._nonscaling_variables + self._scaling_variables
        products = []
        for j in range(self._exponents.cols):
            factors = []
            for var, exp in zip(variables, self._exponents.col(j)):
                factors.append(Power(var, exp))
            products.append(Product(*factors))

        self._variables = tuple(products)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variables = ', '.join(printer._print(var) for var in self._xvariables)
        
        if self._is_nondimensional:
            dimensions = ''
        else:
            dims = []
            for dim_name, dim_exp in self._dimensions.items():
                dim_exp_ = _unsympify_number(dim_exp)
                if isinstance(dim_exp_, str):
                    dim_exp_ = f"'{dim_exp_}'"
                dims.append(f'{dim_name}={dim_exp_}')
            dimensions = f", {', '.join(dims)}"

        return f'{class_name}({variables}{dimensions})'
