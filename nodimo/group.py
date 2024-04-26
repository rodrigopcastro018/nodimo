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

from sympy import sstr, srepr
from sympy.core._print_helpers import Printable

from nodimo.variable import BasicVariable
from nodimo._internal import _show_object, _repr


class Group:  # TODO: Maybe make this inherit from tuple. Or make it work like an iterable object.
    """Group of variables.

    This class contains common attributes and methods that are used by
    classes created with a group of variables.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that constitute the group.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        Tuple with the variables that constitute the group.
    dimensions : tuple[str]
        Tuple with the dimensions' names.
    """

    def __init__(self, *variables: BasicVariable):

        self._variables: tuple[BasicVariable] = variables
        self._dimensions: tuple[str]
        self._set_basicgroup_properties()

    @property
    def variables(self) -> tuple[BasicVariable]:
        return self._variables

    @variables.setter
    def variables(self, variables: tuple[BasicVariable]):
        self._variables = variables
        self._set_basicgroup_properties()

    @property
    def dimensions(self) -> tuple[str]:
        return self._dimensions

    def _set_basicgroup_properties(self):
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
        elif set(self._variables) != set(other.variables):
            return False
        
        return True

    def __contains__(self, item) -> bool:

        return item in self._variables

    def __len__(self) -> int:

        return len(self._variables)

    def __iter__(self) -> tuple:

        return self._variables

    def __str__(self) -> str:

        class_name = type(self).__name__
        variables_str = sstr(self._variables)

        return f'{class_name}{variables_str}'

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variables_repr = _repr(self._variables)

        return f'{class_name}{variables_repr}'


class PrintableGroup(Printable, Group):
    """Printable group of variables.

    Equivalent to Group, but it inherits from the Sympy Printable class
    the ability to be displayed in a pretty format.

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
        """User string representation according to Sympy."""

        return Group.__str__(self)

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        return Group.__repr__(self)

    def _pretty(self, printer) -> str:
        """Pretty representation according to Sympy."""

        return printer._print("'_pretty' method not implemented")

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return R"\text{\textit{\_latex} method not implemented}"
