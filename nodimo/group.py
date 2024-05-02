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

from sympy import sstr, srepr, Rational
from sympy.core._print_helpers import Printable
from typing import Union

from nodimo.variable import Variable, OneVar
from nodimo._internal import _show_object


DimensionType = Union[tuple[str], dict[str, Rational]]


class Collection:  # TODO: I couldn't make it inherit from tuple like I wanted. But sympy has a Tuple class that might work well.
    """Collection of variables.

    This class contains common attributes and methods that are used by
    classes created with a collection of variables.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the collection.

    Attributes
    ----------
    variables : tuple[Variable]
        Tuple with the variables that constitute the collection.
    dimensions : tuple[str] or dict[str, Rational]
        Tuple with the dimensions' names.
    """

    def __init__(self, *variables: Variable):

        self._variables: tuple[Variable] = variables
        self._dimensions: DimensionType
        self._base_variables: tuple[Variable]
        self._has_one: bool
        self._has_product: bool
        self._is_independent: bool
        self._set_collection_properties()

    @property
    def variables(self) -> tuple[Variable]:
        return self._variables

    @property
    def dimensions(self) -> DimensionType:
        return self._dimensions

    def _set_collection_properties(self):
        """Sets the collection properties."""

        self._has_one = False
        self._has_product = False
        self._is_independent = False
        self._set_base_variables()
        self._set_dimensions()

    def _set_dimensions(self):
        """Sets the dimensions' names."""

        dimensions = []

        for var in self._variables:
            for dim in var.dimensions.keys():
                if dim not in dimensions:
                    dimensions.append(dim)

        self._dimensions = tuple(dimensions)

    @classmethod
    def _clear_ones(self, *variables: Variable) -> tuple[Variable]:
        """Removes instances of OneVar."""

        new_variables = []
        for var in variables:
            if not isinstance(var, OneVar):
                new_variables.append(var)

        return tuple(new_variables)

    def _set_base_variables(self):
        """Determines the base variables.

        Base variables are instances of Variable (and CombinedVariable).  # TODO: Maybe I'll have to drop this combined variable
        """

        from .product import Product
        from .power import Power

        disassembled_variables = []
        for var in self._variables:
            if isinstance(var, Product):
                disassembled_variables.extend(var._variables)
                self._has_product = True
            elif isinstance(var, OneVar):
                self._has_one = True
            else:
                disassembled_variables.append(var)

        # Attribute to be used by the BasicProduct class.
        self._disassembled_variables = tuple(disassembled_variables)

        # Store base variables, keeping the order.
        base_variables = []
        for var in disassembled_variables:
            if isinstance(var, Power):
                base_var = var._variable
            else:
                base_var = var
            
            if base_var not in base_variables:
                base_variables.append(base_var)

        self._base_variables = tuple(base_variables)
        self._is_independent = len(self._base_variables) == len(self._variables)

    def __eq__(self, other) -> bool:

        if self is other:
            return True
        elif not isinstance(other, type(self)):
            return False
        elif set(self._variables) != set(other.variables):
            return False
        
        return True
    
    def __contains__(self, item) -> bool:

        return self._variables.__contains__(item)

    def __len__(self) -> int:

        return self._variables.__len__()

    def __iter__(self):

        return self._variables.__iter__()

    def __next__(self):

        return self.__iter__().__next__() 

    def __str__(self) -> str:

        class_name = type(self).__name__
        variables_str = sstr(self._variables)

        return f'{class_name}{variables_str}'

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variables_repr = srepr(self._variables)

        return f'{class_name}{variables_repr}'


class Group(Collection):  # TODO: Maybe change variables from tuple to frozenset?
    """Group of variables.

    Equivalent to a Collection without duplicate variables.
    """

    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._set_group_properties()

    def _set_group_properties(self):  # TODO: Change this later to _set_group_properties
        """Sets the group properties."""

        if not self._is_independent:
            self._remove_duplicate_variables()
            self._set_collection_properties()

    def _remove_duplicate_variables(self):
        """Removes duplicate variables, keeping the order."""

        new_variables = []
        
        for var in self._variables:
            if var not in new_variables:
                new_variables.append(var)

        self._variables = tuple(new_variables)


class PrintableGroup(Group, Printable):
    """Printable group of variables.

    Equivalent to Group, but it inherits from the Sympy Printable class
    the ability to be displayed in a pretty format.

    Methods
    -------
    show()
        Displays the group in a pretty format.
    """

    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._symbolic: Printable
        self._set_printgroup_properties()

    @property
    def symbolic(self) -> Printable:
        return self._symbolic

    def show(self):
        """Displays the group in a pretty format."""

        _show_object(self)

    def _set_printgroup_properties(self):
        """Sets the printable group properties."""

        self._build_symbolic()
    
    def _build_symbolic(self):
        """Builds symbolic representation in Sympy."""

        from sympy import Tuple

        self._symbolic = Tuple(*self._variables)

    def _sympy_(self):
        """Sympified group."""

        return self._symbolic

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        return super().__repr__()

    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy."""

        return printer._print(self._symbolic)

    _latex = _pretty = _sympystr
