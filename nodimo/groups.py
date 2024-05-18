"""
===========================
Basic (:mod:`nodimo.basic`)
===========================

This module contains base classes for Nodimo.

Classes
-------
BasicGroup
    Base class for classes created with variables.
"""

from sympy import Matrix, zeros, eye
from sympy.printing.pretty.stringpict import prettyForm
from typing import Optional

from nodimo.variable import Variable
from nodimo.collection import Collection
from nodimo.power import Power
from nodimo.product import Product
from nodimo._internal import _show_warning, UnrelatedVariableWarning


class Group(Collection):
    """Group of variables.

    Equivalent to a Collection without duplicate variables.
    """

    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._set_group()

    def _set_group(self):
        self._clear_duplicate_variables()

    def _clear_duplicate_variables(self):
        clear_variables = []
        for var in self._variables:
            if var not in clear_variables:
                clear_variables.append(var)

        self._variables = tuple(clear_variables)


class HomogeneousGroup(Group):
    """Dimensionally homogeneous group of variables.

    Equivalent to a dimmensionally homogenous Group.

    Warns
    -----
    UnrelatedVariableWarning
        Discarded variables.
    """

    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._set_homogeneous_group()

    def _set_homogeneous_group(self):
        self._clear_heterogeneous_variables()

    def _clear_heterogeneous_variables(self):
        clear_variables = list(self._variables)
        heterogenous_variables = []
        for _ in self._variables:
            self._set_matrix()
            var = None
            for row in self._raw_matrix:
                row_bool = [bool(exp) for exp in row]
                if sum(row_bool) == 1:
                    var = clear_variables[row_bool.index(True)]
                    if var not in heterogenous_variables:
                        heterogenous_variables.append(var)
                        clear_variables.remove(var)
                        self._variables = tuple(clear_variables)
                        self._set_collection_dimensions()
                        break
            if var is None:
                break

        if len(heterogenous_variables) > 0:
            _show_warning(f"Discarded variables ({str(heterogenous_variables)[1:-1]})",
                          UnrelatedVariableWarning)


class ScalingGroup(Group):
    """TODO
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
            raise ValueError("Scaling variables are not dimensionally independent")

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variables_repr = ', '.join(printer._print(var) for var in self._variables)
        id_number_repr = f', id_number={self._id_number}' if self._id_number else ''

        return f'{class_name}({variables_repr}{id_number_repr})'

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


class TransformationGroup(HomogeneousGroup):  # TODO: What if the group has no scaling variables?
    """Blueprint for the transformation of a homogeneous group.  # TODO: Think about merging this class with DimensionalGroup

    A TransformationGroup sets the layout fot the transformation of a
    group of variables into another group by using scaling variables as
    transformation parameters. Every variable of the new group is a
    product between one nonscaling variable and the set of scaling
    variables.

    Raises
    ------
    ValueError
        If the number of scaling variables is not adequate or if the
        scaling variables do not form an independent set.
    """
    
    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._xvariables: tuple[Variable]
        self._set_transformation_group()

    def _set_transformation_group(self):
        self._set_scaling_variables()
        self._set_matrix_independent_rows()
        self._set_matrix()  # TODO: Decide. It's either this or redo HomogeneousGroup._clear_unrelated_variables
        self._set_submatrices()
        self._set_scaling_matrix()
        self._validate_transformation_group()
        self._xvariables = tuple(list(self._variables))

    def _set_scaling_matrix(self):
        """Builds scaling and nonscaling matrices."""

        scaling_matrix = self._get_submatrix(*self._scaling_variables)
        nonscaling_matrix = self._get_submatrix(*self._nonscaling_variables)

        self._scaling_matrix = scaling_matrix[self._independent_rows, :]
        self._nonscaling_matrix = nonscaling_matrix[self._independent_rows, :]

    def _validate_transformation_group(self):
        check1 = len(self._scaling_variables) == self._rank
        check2 = self._scaling_matrix.rank() == self._rank
        if not check1 or not check2:
            raise ValueError(
                f"The group must have {self._rank} "
                f"dimensionally independent scaling variables"
            )


class DimensionalGroup(HomogeneousGroup):
    """Dimensional group created from a homogeneous group.

    This class creates a group of dimensional variables from a
    homogeneous given group of variables. It does that using the
    TransformationGroup layout. The resulting group has all variables
    with the same dimension.
    """

    def __init__(self, *variables: Variable, **dimensions: int):
        super().__init__(*variables)
        self._is_nondimensional: bool
        self._xvariables: tuple[Variable] = self._variables
        self._set_dimensional_group_dimensions(**dimensions)
        self._set_dimensional_group()

    def _set_dimensional_group(self):
        self._set_scaling_variables()
        self._set_matrix()  # TODO: Decide. It's either this or redo HomogeneousGroup._clear_unrelated_variables
        self._set_matrix_independent_rows()
        self._set_submatrices()
        self._set_scaling_matrix()
        self._validate_dimensional_group()
        self._set_exponent_matrix()
        self._set_dimensional_group_variables()

    def _set_dimensional_group_dimensions(self, **dimensions: int):
        var = Variable('', **dimensions)

        if not set(var.dimensions).issubset(set(self._dimensions)):
            invalid_dimensions = []
            for dim in var.dimensions:
                if dim not in self._dimensions:
                    invalid_dimensions.append(dim)
            raise ValueError(f"Invalid dimensions ({str(invalid_dimensions)[1:-1]})")

        group_dimensions = {}
        for dim in self._dimensions:
            if dim in var.dimensions:
                group_dimensions[dim] = var.dimensions[dim]
            else:
                group_dimensions[dim] = S.Zero

        self._dimensions = group_dimensions
        self._is_nondimensional = var.is_nondimensional

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

        return f'{class_name}({variables})'


class NonDimensionalGroup(TransformationGroup):
    """Nondimensional group created from a homogeneous group.

    This class creates a group of nondimensinal variables from a
    homogeneous given group of variables. It does that using the
    TransformationGroup layout.
    """
    
    def __init__(self, *variables: Variable):
        super(TransformationGroup, self).__init__(*variables)
        self._products: tuple[Variable]
        self._set_nondimensional_group()

    def _set_nondimensional_group(self):
        self._set_dimensional_variables()
        self._variables = self._dimensional_variables
        self._set_transformation_group()
        self._variables = self._nondimensional_variables
        self._set_exponents()
        self._set_products()
        self._set_collection_dimensions()

    def _set_exponents(self):
        """Determines the exponent of each variable, for every product.

        References
        ----------
        .. [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
               (Butterworth-Heinemann, 2007), p. 133.
        """

        nvars = len(self._xvariables)
        rank = self._rank

        A = self._scaling_matrix
        B = self._nonscaling_matrix

        E11 = eye(nvars - rank)
        E12 = zeros(nvars - rank, rank)
        E21 = -A**-1 * B
        E22 = A**-1
        E = Matrix([[E11, E12],
                    [E21, E22]])

        Z1 = eye(nvars - rank)
        Z2 = zeros(rank, nvars - rank)
        Z = Matrix([[Z1],
                    [Z2]])

        exponents = E * Z

        self._exponents = exponents.as_immutable()

    def _set_products(self):
        variables = self._nonscaling_variables + self._scaling_variables
        products = []
        for j in range(len(self._nonscaling_variables)):
            factors = []
            for var, exp in zip(variables, self._exponents.col(j)):
                factors.append(Power(var, exp))
            products.append(Product(*factors))

        self._products = tuple(products)
        self._variables += self._products
