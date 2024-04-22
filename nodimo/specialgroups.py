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
from sympy import ImmutableDenseMatrix

from nodimo.variable import BasicVariable
from nodimo.group import Group
from nodimo.matrix import BasicDimensionalMatrix, DimensionalMatrix
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

    def __init__(self, *variables: BasicVariable):
        
        super().__init__(*variables)
        self._set_homogroup_properties()

    @Group.variables.setter
    def variables(self, variables: tuple[BasicVariable]):
        self._variables = variables
        self._set_basicgroup_properties()
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


# class TransformableGroup(HomogeneousGroup):
#     """Homogeneous group that can be transformed into another group.

#     A TransformableGroup can be transformed into another group by using
#     its scaling variables as tranformation parameters. Every variable of
#     the new group is a product between one nonscaling variable and the
#     set of scaling variables.

#     Parameters
#     ----------
#     *variables : BasicVariable
#         Variables that constitute the group.

#     Attributes
#     ----------
#     variables : tuple[BasicVariable]
#         Tuple with the variables.
#     dimensions : tuple[str]
#         Tuple with the dimensions' names.
#     scaling_variables : tuple[BasicVariable]
#         Tuple with scaling variables.
#     nonscaling_variables : tuple[BasicVariable]
#         Tuple with nonscaling variables.

#     Methods
#     -------
#     show()
#         Displays the group in a pretty format.

#     Raises
#     ------
#     ValueError
#         If the number of scaling variables is not adequate.
#     ValueError
#         If the scaling variables do not form an independent set.
#     """
    
#     def __init__(self, *variables: BasicVariable):

#         super().__init__(*variables)

#         self._scaling_variables: BasicVariable
#         self._nonscaling_variables: BasicVariable
#         self._dimensional_matrix: DimensionalMatrix
#         self._nonscaling_matrix: ImmutableDenseMatrix
#         self._scaling_matrix: ImmutableDenseMatrix

#     @HomogeneousGroup.variables.setter
#     def variables(self, variables: tuple[BasicVariable]):
#         self._variables = variables
#         super()._set_properties()
#         self._set_properties()

#     @property
#     def scaling_variables(self) -> tuple[BasicVariable]:
#         return self._scaling_variables

#     @property
#     def nonscaling_variables(self) -> tuple[BasicVariable]:
#         return self._nonscaling_variables

#     def _set_properties(self):
#         """Sets the group properties."""
        
#         self._separate_variables()
#         self._build_matrices()
#         self._validate_group()

#     def _separate_variables(self):
#         self._scaling_variables = []
#         self._nonscaling_variables = []
#         for var in self.variables:
#             if var.is_scaling:
#                 self._scaling_variables.append(var)
#             else:
#                 self._nonscaling_variables.append(var)
#         self._variables = tuple(self._nonscaling_variables + self._scaling_variables)

#     def _build_matrices(self):
#         self._dimensional_matrix = DimensionalMatrix(*self.variables)
#         independent_rows = self._dimensional_matrix.independent_rows
#         nonscaling_matrix = BasicDimensionalMatrix(*self.nonscaling_variables).matrix
#         scaling_matrix = BasicDimensionalMatrix(*self.scaling_variables).matrix
#         self._nonscaling_matrix = nonscaling_matrix[independent_rows, :]
#         self._scaling_matrix = scaling_matrix[independent_rows, :]

#     def _validate_group(self):
#         """Validates the given scaling variables."""
        
#         if len(self._scaling_variables) != self._dimensional_matrix.rank:
#             raise ValueError(
#                 f"The group must have {self._dimensional_matrix.rank} scaling variables."
#             )
#         elif self._scaling_matrix.rank() != self._dimensional_matrix.rank:
#             raise ValueError("Scaling variables do not form an independent set")
    
#     def _sympystr(self, printer) -> str:
#         """String representation according to Sympy."""
        
#         return f"Scaling variables: {sp.pretty(self.scaling_variables)[1:-1]}"

#     def _latex(self, printer) -> str:
#         """Latex representation according to Sympy."""

#         scvars_latex = R',\ '.join([sp.latex(var) for var in self.scaling_variables])

#         return R"\text{Scaling variables: } " + scvars_latex


# An generalization to be implemented later.
# class DimensionalGroup(Group):
# 
#     def __init__(self, scaling_group: ScalingGroup, dimensions: Optional[dict[str, int]] = {}):  # dimensions == {} must be equivalent to NonDimensionalGroup implementation
# 
#         pass


# class NonDimensionalGroup(Group):  # When DimensionalGroup is implemented, this should inherit from it.
#     """Blablabla.

#     blablabla.

#     Parameters
#     ----------
#     *scaling_group : ScalingGroup
#         Variables that constitute the group.

#     Attributes
#     ----------
#     variables : tuple[BasicVariable]
#         Tuple with the variables.
#     dimensions : tuple[str]
#         Tuple with the dimensions' names.

#     Methods
#     -------
#     show()
#         Displays the group in a pretty format.
#     """
    
#     def __init__(self, transformable_group: TransformableGroup):

#         self._transformable_group: TransformableGroup = transformable_group
#         self._variables: BasicVariable
#         self._separate_variables()
#         self._calculate_exponents()
    
#     @property
#     def transformable_group(self) -> TransformableGroup:
#         return self._transformable_group

#     def _separate_variables(self):
#         """."""
        
#         dimensional_variables = []
#         nondimensional_variables = []
#         for var in self._transformable_group.variables:
#             if var.is_nondimensional:
#                 nondimensional_variables.append(var)
#             else:
#                 dimensional_variables.append(var)

#         self._transformable_group.variables = tuple(dimensional_variables)
#         self._variables = tuple(nondimensional_variables)

#     def _calculate_exponents(self):
#         """Determines the exponents to build the nondimensional products.

#         References
#         ----------
#         .. [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
#                (Butterworth-Heinemann, 2007), p. 133.
#         """

#         nvars = len(self._transformable_group.variables)
#         rank = self._transformable_group._dimensional_matrix.rank

#         A = self.transformable_group._scaling_matrix
#         B = self.transformable_group._nonscaling_matrix

#         E11 = sp.eye(nvars - rank)
#         E12 = sp.zeros(nvars - rank, rank)
#         E21 = -A**-1 * B
#         E22 = A**-1
#         E = sp.Matrix([[E11, E12],
#                        [E21, E22]])

#         Z1 = sp.eye(nvars - rank)
#         Z2 = sp.zeros(rank, nvars - rank)
#         Z = sp.Matrix([[Z1],
#                        [Z2]])

#         exponents = E * Z
        
#         self._exponents = exponents.as_immutable()
