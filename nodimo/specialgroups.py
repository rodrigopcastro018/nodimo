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

import sympy as sp
from sympy import sstr, srepr, ImmutableDenseMatrix

from nodimo.variable import Variable
from nodimo.group import Group
from nodimo.matrix import BasicDimensionalMatrix, DimensionalMatrix
from nodimo.power import Power
from nodimo.product import Product
from nodimo._internal import _show_warning, UnrelatedVariableWarning


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
        self._set_homogroup_properties()

    def _set_homogroup_properties(self):
        """Sets the group properties."""

        self._clear_unrelated_variables()
        self._set_dimensions()

    def _clear_unrelated_variables(self):
        """Removes unrelated variables.

        Unrelated variables are the only ones in the set of variables to have
        a particular dimension.
        """

        clear_variables = list(self._variables)
        unrelated_variables = []

        for _ in self._dimensions:
            dimensional_matrix = BasicDimensionalMatrix(*clear_variables)._raw_matrix
            unr_var = None

            for row in dimensional_matrix:
                row_bool = [bool(exp) for exp in row]
                if sum(row_bool) == 1:
                    unr_var = clear_variables[row_bool.index(True)]
                    if unr_var not in unrelated_variables:
                        unrelated_variables.append(unr_var)
                        clear_variables.remove(unr_var)

            if unr_var is None:
                break

        if len(unrelated_variables) > 0:
            _show_warning(f"Discarded variables → "
                          f"{sp.pretty(unrelated_variables)[1:-1]}",
                          UnrelatedVariableWarning)

            self._variables = tuple(clear_variables)


class TransformationGroup(HomogeneousGroup):
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
        self._set_transfgroup_properties()
        
        self._xvariables: tuple[Variable]
        self._scaling_variables: tuple[Variable]
        self._nonscaling_variables: tuple[Variable]
        self._dimensional_matrix: DimensionalMatrix
        self._nonscaling_matrix: ImmutableDenseMatrix
        self._scaling_matrix: ImmutableDenseMatrix

    # Redefining variables as a read-only property
    @property
    def variables(self) -> tuple[Variable]:
        return self._variables

    @property
    def xvariables(self) -> tuple[Variable]:
        return self._xvariables

    @property
    def scaling_variables(self) -> tuple[Variable]:
        return self._scaling_variables

    @property
    def nonscaling_variables(self) -> tuple[Variable]:
        return self._nonscaling_variables

    def _set_transfgroup_properties(self):
        """Sets the group properties."""

        self._separate_scaling_variables()
        self._build_matrices()
        self._validate_group()
        self._xvariables = tuple(list(self._variables))
        self._variables = ()
        self._dimensions = {}

    def _separate_scaling_variables(self):
        """Separates variables into scaling and nonscaling."""
        
        scaling_variables = []
        nonscaling_variables = []
        for var in self._variables:
            if var.is_scaling:
                scaling_variables.append(var)
            else:
                nonscaling_variables.append(var)

        self._nonscaling_variables = tuple(nonscaling_variables)
        self._scaling_variables = tuple(scaling_variables)
        self._variables = self._nonscaling_variables + self._scaling_variables

    def _build_matrices(self):
        """Builds scaling and nonscaling matrices."""
        
        self._dimensional_matrix = BasicDimensionalMatrix(*self._variables)
        self._dimensional_matrix._set_independent_rows()
        independent_rows = self._dimensional_matrix._independent_rows

        nonscaling_matrix = self._dimensional_matrix._get_submatrix(*self._nonscaling_variables)
        scaling_matrix = self._dimensional_matrix._get_submatrix(*self._scaling_variables)
        self._nonscaling_matrix = nonscaling_matrix[independent_rows, :]
        self._scaling_matrix = scaling_matrix[independent_rows, :]

    def _validate_group(self):
        """Validates the scaling variables."""
        
        if len(self._scaling_variables) != self._dimensional_matrix.rank:
            raise ValueError(
                f"The group must have {self._dimensional_matrix.rank} scaling variables."
            )
        elif self._scaling_matrix.rank() != self._dimensional_matrix.rank:
            raise ValueError("Scaling variables do not form a dimensionally independent set")

    def __eq__(self, other) -> bool:

        if self is other:
            return True
        elif not isinstance(other, type(self)):
            return False
        elif set(self._xvariables) != set(other.xvariables):
            return False

        return True

    def __str__(self) -> str:

        class_name = type(self).__name__
        variables_str = sstr(self._xvariables)

        return f'{class_name}{variables_str}'

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variables_repr = srepr(self._xvariables)

        return f'{class_name}{variables_repr}'

# An generalization to be implemented later.
# class DimensionalGroup(Group):
# 
#     def __init__(self, scaling_group: ScalingGroup, dimensions: Optional[dict[str, int]] = {}):  # dimensions == {} must be equivalent to NonDimensionalGroup implementation
# 
#         pass


class NonDimensionalGroup(TransformationGroup):  # When DimensionalGroup is implemented, this should inherit from it.
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

        super().__init__(*variables)
        self._nondim_products: tuple[Variable]
        self._set_nondimgroup_properties()
    
    def _set_nondimgroup_properties(self):
        """Sets the group properties."""
        
        self._separate_dimensional_variables()
        self._calculate_exponents()
        self._build_nondimensional_products()
    
    def _separate_dimensional_variables(self):
        """Retains already nondimensional variables."""
        
        dimensional_variables = []
        nondimensional_variables = []
        for var in self._xvariables:
            if var.is_nondimensional:
                nondimensional_variables.append(var)
            else:
                dimensional_variables.append(var)

        if len(nondimensional_variables) > 0:
            self.xvariables = tuple(dimensional_variables)
            self._variables = tuple(nondimensional_variables)

    def _calculate_exponents(self):
        """Determines the exponents for the scaling variables.

        References
        ----------
        .. [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
               (Butterworth-Heinemann, 2007), p. 133.
        """

        nvars = len(self._xvariables)
        rank = self._dimensional_matrix.rank

        A = self._scaling_matrix
        B = self._nonscaling_matrix

        E11 = sp.eye(nvars - rank)
        E12 = sp.zeros(nvars - rank, rank)
        E21 = -A**-1 * B
        E22 = A**-1
        E = sp.Matrix([[E11, E12],
                       [E21, E22]])

        Z1 = sp.eye(nvars - rank)
        Z2 = sp.zeros(rank, nvars - rank)
        Z = sp.Matrix([[Z1],
                       [Z2]])

        exponents = E * Z
        
        self._exponents = exponents.as_immutable()

    def _build_nondimensional_products(self):
        """Builds the nondimensional variables."""

        self._calculate_exponents()
        nondim_products = []

        for j in range(len(self._nonscaling_variables)):
            factors = []
            for var, exp in zip(self._xvariables, self._exponents.col(j)):
                factors.append(Power(var, exp))
            nondim_products.append(Product(*factors))

        self._nondim_products = tuple(nondim_products)
        self._variables += self._nondim_products

    def _set_asdependent_from_arguments(self):
        """Sets nondimensional products as dependent from arguments.

        Nondimensional product is set as dependent if it contains at
        least one dependent variable in its expression.
        """

        for prod in self._nondim_products:
            prod.is_dependent = any(var.is_dependent for var in prod._variables)

    def __eq__(self, other) -> bool:

        return super(TransformationGroup, self).__eq__(other)
