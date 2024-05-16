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

from sympy import Rational, Matrix, zeros, eye
from sympy.printing.pretty.stringpict import prettyForm
from typing import Union, Optional

from nodimo.variable import Variable
from nodimo.collection import Collection
from nodimo.power import Power
from nodimo.product import Product
from nodimo._internal import _show_warning, UnrelatedVariableWarning


DimensionType = Union[tuple[str], dict[str, Rational]]


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
        """Removes duplicate variables, keeping the order."""

        clear_variables = []
        for var in self._variables:
            if var not in clear_variables:
                clear_variables.append(var)

        self._variables = tuple(clear_variables)


class HomogeneousGroup(Group):
    """Dimensionally homogeneous group of variables.

    Equivalent to Group, but it is dimmensionally homogenous.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that constitute the group.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        Tuple with the variables.
    dimensions : tuple[str]
        Tuple with the dimensions' names.

    Warns
    -----
    UnrelatedVariableWarning
        Discarded variables.
    """

    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._set_homogeneous_group()

    def _set_homogeneous_group(self):
        self._clear_unrelated_variables()

    def _clear_unrelated_variables(self):
        """Removes unrelated variables.

        Unrelated variables are the only ones in the set of variables to have
        a particular dimension.
        """

        clear_variables = list(self._variables)
        unrelated_variables = []
        for _ in self._variables:
            self._set_matrix()
            unr_var = None
            for row in self._raw_matrix:
                row_bool = [bool(exp) for exp in row]
                if sum(row_bool) == 1:
                    unr_var = clear_variables[row_bool.index(True)]
                    if unr_var not in unrelated_variables:
                        unrelated_variables.append(unr_var)
                        clear_variables.remove(unr_var)
                        self._variables = tuple(clear_variables)
                        self._set_collection_dimensions()
                        break
            if unr_var is None:
                break

        if len(unrelated_variables) > 0:
            _show_warning(f"Discarded variables "
                          f"({str(unrelated_variables)[1:-1]})",
                          UnrelatedVariableWarning)


class ScalingGroup(Group):

    def __init__(self, *variables: Variable, id_number: Optional[int] = None):

        super().__init__(*variables)
        self._id_number: int = id_number
        self._set_scaling_group()

    def _set_scaling_group(self):
        self._clear_ones()  # TODO: Find a better place to put this.
        self._set_scgroup_variables()
        self._set_matrix_rank()
        self._validate_scaling_group()

    def _set_scgroup_variables(self):
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
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join(printer._print(var) for var in self._variables)
        id_number_repr = f', id_number={self._id_number}' if self._id_number else ''

        return f'{class_name}({variables_repr}{id_number_repr})'

    def _sympystr(self, printer):
        """User string representation according to Sympy."""

        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")
        variables = printer._print(self._variables)

        return scgroup + variables

    def _pretty(self, printer):
        """Pretty representation according to Sympy."""

        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")
        variables = printer._print(self._variables)

        return prettyForm(*scgroup.right(variables))

    _latex = _sympystr


class TransformationGroup(HomogeneousGroup):  # TODO: What if the group has no scaling variables?
    """Blueprint for the transformation of a homogeneous group.

    A TransformationGroup sets the layout fot the transformation of a
    group of variables into another group by using scaling variables as
    transformation parameters. Every variable of the new group is a
    product between one nonscaling variable and the set of scaling
    variables.

    Parameters
    ----------
    *variables : BasicVariable
        Variables to be transformed.

    Attributes
    ----------
    variables : empty tuple
        Tuple to be populated with the transformation result.
    dimensions : empty dictionary
        Dictionary to be populated with the transformation result.
    xvariables : tuple[BasicVariable]
        Tuple with the variables to be transformed.
    scaling_variables : tuple[BasicVariable]
        Tuple with scaling variables.
    nonscaling_variables : tuple[BasicVariable]
        Tuple with nonscaling variables.

    Raises
    ------
    ValueError
        If the number of scaling variables is not adequate.
    ValueError
        If the scaling variables do not form an independent set.
    """
    
    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._xvariables: tuple[Variable]
        self._set_transformation_group()

    def _set_transformation_group(self):
        self._set_scaling_variables()
        self._set_matrix_independent_rows()
        self._set_scaling_matrix()
        self._validate_transformation_group()
        self._xvariables = tuple(list(self._variables))

    def _set_scaling_matrix(self):
        """Builds scaling and nonscaling matrices."""

        self._set_matrix()  # TODO: Decide. It's either this or redo HomogeneousGroup._clear_unrelated_variables
        self._set_submatrices()
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


# An generalization to be implemented later.
# class DimensionalGroup(Group):
# 
#     def __init__(self, scaling_group: ScalingGroup, dimensions: Optional[dict[str, int]] = {}):  # dimensions == {} must be equivalent to NonDimensionalGroup implementation
# 
#         pass


class NonDimensionalGroup(TransformationGroup):
    """Nondimensional group created from a homogeneous group.

    This class creates a group of nondimensinal variables from a
    homogeneous given group of variables. It does that using the
    TransformationGroup layout.

    Parameters
    ----------
    *variables : BasicVariable
        Variables to be transformed.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        Tuple with nondimensional variables.
    dimensions : dict[str, int]
        Empty dictionary that represents the nondimensional group.
    xvariables : tuple[BasicVariable]
        Tuple with the variables to be transformed.
    scaling_variables : tuple[BasicVariable]
        Tuple with scaling variables.
    nonscaling_variables : tuple[BasicVariable]
        Tuple with nonscaling variables.

    Raises
    ------
    ValueError
        If the number of scaling variables is not adequate.
    ValueError
        If the scaling variables do not form an independent set.
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
        self._calculate_exponents()
        self._build_nondimensional_products()
        self._set_collection_dimensions()

    def _calculate_exponents(self):
        """Determines the exponents for the scaling variables.

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

    def _build_nondimensional_products(self):
        variables = self._nonscaling_variables + self._scaling_variables
        self._calculate_exponents()
        products = []

        for j in range(len(self._nonscaling_variables)):
            factors = []
            for var, exp in zip(variables, self._exponents.col(j)):
                factors.append(Power(var, exp))
            products.append(Product(*factors))

        self._products = tuple(products)
        self._variables += self._products
