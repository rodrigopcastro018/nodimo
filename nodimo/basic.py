"""
===========================
Basic (:mod:`nodimo.basic`)
===========================

This module contains the base class for some of Nodimo's classes.

Classes
-------
Basic
    Base class for some of the Nodimo's classes.
"""

from sympy import srepr
from sympy.core._print_helpers import Printable
# from typing import Union

# from nodimo.variable import Variable
# from nodimo.group import VariableGroup
from nodimo._internal import (_show_object,
                              _remove_duplicates,
                              _obtain_dimensions)


# VariableOrGroup = Union[Variable, VariableGroup]


class BasicVariable:
    """Creates a basic variable.

    This is the most basic element as it is part of all the other
    classes in Nodimo. It contains a few attributes that are useful in
    describing dimensional properties.

    Parameters  
    ----------
    dependent : bool, default=False
        If ``True``, the variable is dependent.
    scaling : bool, default=False
        If ``True``, the variable can be used as scaling parameter.
    **dimensions : int
        The dimensions of the variable given as keyword arguments.

    Attributes
    ----------
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the variable is dependent.
    is_scaling : bool
        If ``True``, the variable can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the variable is nondimensional.

    Raises
    ------
    ValueError
        If the variable is set as both dependent and scaling.
    ValueError
        If the variable is set as scaling, but with no dimensions.
    """

    def __init__(self,
                 dependent: bool = False,
                 scaling: bool = False,
                 **dimensions: int):

        self.dimensions: dict[str, int] = dimensions
        self.is_dependent: bool = dependent
        self.is_scaling: bool = scaling
        self.is_nondimensional: bool = all(dim == 0
                                           for dim in self.dimensions.values())

        self._validate_variable()

    def _validate_variable(self) -> None:
        """Validates variable's arguments.
        
        Raises
        ------
        ValueError
            If the variable is set as both dependent and scaling.
        ValueError
            If the variable is set as scaling, but with no dimensions.
        """

        if self.is_dependent and self.is_scaling:
            raise ValueError(
                "A variable can not be both dependent and scaling")
        
        elif self.is_scaling and self.is_nondimensional:
            raise ValueError(
                "A variable can not be both scaling and nondimensional")


class Basic(Printable):
    """Base class for some of the Nodimo's classes.

    This base class groups some common attributes and methods used by
    some Nodimo's classes. It inherits from the Sympy Printable class
    the ability to display mathematical expressions in a pretty format.

    Parameters
    ----------
    *variables : Variable or VariableGroup
        Variables or groups that constitute the Basic class.

    Attributes
    ----------
    variables : list[Variable or VariableGroup]
        List of variables or groups used by the Basic class.
    dimensions : list[str]
        List with dimensions' names of the given variables or groups.
    """

    def __init__(self,
                 *variables: BasicVariable,
                 get_dimensions: bool = True):

        self.variables: list[BasicVariable]
        self.variables = _remove_duplicates(list(variables))

        if get_dimensions:
            self.dimensions: list[str] = _obtain_dimensions(*variables)
    
    def show(self) -> None:
        """Displays the object in pretty format."""

        _show_object(self)

    def __eq__(self, other) -> bool:

        if self is other:
            return True
        elif not isinstance(other, type(self)):
            return False
        elif set(self.variables) != set(other.variables):
            return False
        
        return True
    
    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return "'_sympystr' method not implemented yet"

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join([srepr(var) for var in self.variables])

        return (f'{class_name}('
                + variables_repr
                + ')')

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return R"\text{\textit{\_latex} method not implemented yet}"

    # From the the function module. I'll leave here for a moment
    # and delete when i'm done with this part of the code.
    #
    # from sympy.printing.pretty.pretty import PrettyPrinter
    #
    # I was defining _pretty as below and making _sympystr = _pretty.
    # It works, but it looks so wrong.
    #
    # def _pretty(self, printer) -> str:
    #     """Pretty string representation according to Sympy."""

    #     return PrettyPrinter(
    #         settings={'root_notation': False}
    #     )._print(self.function)

    # _sympystr = _pretty

    # In the _latex method:
    # Perhaps, this is the correct way of doing it, but i'm afraid i'll
    # lose the root_notation setting (issue #33)
    # return printer._print(self.function)
