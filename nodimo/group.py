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

from sympy import srepr
from sympy.core._print_helpers import Printable

from nodimo.variable import BasicVariable
from nodimo._internal import _show_object


class BasicGroup:
    """Basic group of variables.

    This class contains common attributes and methods that are used by
    classes created with a group of variables.

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
    """

    def __init__(self, *variables: BasicVariable):

        self._variables: tuple[BasicVariable] = variables
        self._dimensions: tuple[str]
        self.variables = self._variables  # First check in

    @property
    def variables(self) -> tuple[BasicVariable]:
        return self._variables

    @variables.setter
    def variables(self, variables: tuple[BasicVariable]):
        self._variables = variables
        self._set_properties()

    @property
    def dimensions(self) -> tuple[str]:
        return self._dimensions

    def _set_properties(self):
        """Sets the group properties."""

        self._remove_duplicate_variables()
        self._set_dimensions()

    def _remove_duplicate_variables(self):
        """Removes duplicate variables."""

        new_variables = []
        
        for var in self.variables:
            if var not in new_variables:
                new_variables.append(var)

        self._variables = tuple(new_variables)
    
    def _set_dimensions(self):
        """Set the dimensions' names."""
    
        dimensions = []
    
        for var in self.variables:
            for dim in var.dimensions.keys():
                if dim not in dimensions:
                    dimensions.append(dim)
    
        self._dimensions = tuple(dimensions)

    def __eq__(self, other) -> bool:

        if self is other:
            return True
        elif not isinstance(other, type(self)):
            return False
        elif set(self.variables) != set(other.variables):
            return False
        
        return True


class Group(BasicGroup, Printable):
    """Group of variables.

    Equivalent to BasicGroup, but it inherits from the Sympy Printable
    class the ability to display mathematical expressions in a pretty
    format.

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

    Methods
    -------
    show()
        Displays the group in a pretty format.
    """

    def __init__(self, *variables: BasicVariable):

        super().__init__(*variables)
    
    def show(self):
        """Displays the group in a pretty format."""

        _show_object(self)
    
    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return "'_sympystr' method not implemented yet"

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = srepr(self._variables)[1:-1]

        return (f'{class_name}('
                + variables_repr
                + ')')

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return R"\text{\textit{\_latex} method not implemented yet}"


# class HomogeneousGroup(Group):
#     """Dimensionally homogeneous group of variables.

#     Equivalent to Group, but it is dimmensionally homogenous.

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

#     Methods
#     -------
#     show()
#         Displays the group in a pretty format.

#     Warns
#     -----
#     UnrelatedVariableWarning
#         Discarded variables.
#     """

#     def __init__(self, *variables: BasicVariable):
#         super().__init__(*variables)

#     @Group.variables.setter
#     def variables(self, variables: tuple[BasicVariable]):
#         self._variables = variables
#         self._set_properties()

#     def _set_properties(self):
#         """Sets the group properties."""

#         self._remove_duplicate_variables()
#         self._clear_unrelated_variables()
#         self._set_dimensions()
    
#     def _clear_unrelated_variables(self):
#         """Removes unrelated variables.

#         Unrelated variables are the only ones in the set of variables to have
#         a particular dimension.
#         """

#         dimensional_matrix = BasicDimensionalMatrix(*self._variables)._raw_matrix

#         clear_variables = list(self._variables)
#         unrelated_variables = []
    
#         for row in dimensional_matrix:
#             row_bool = [bool(exp) for exp in row]
#             if sum(row_bool) == 1:
#                 var = self._variables[row_bool.index(True)]
#                 if var not in unrelated_variables:
#                     unrelated_variables.append(var)
#                     clear_variables.remove(var)
        
#         if len(unrelated_variables) > 0:
#             _show_warning(f"Discarded variables → "
#                           f"{pretty(unrelated_variables)[1:-1]}",
#                           UnrelatedVariableWarning)
    
#             self._variables = tuple(clear_variables)


# class ScalingGroup(HomogeneousGroup):
#     pass

#class NondimensionalGroup(): ???