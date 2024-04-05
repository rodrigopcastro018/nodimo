"""TODO
"""

from sympy import srepr
from sympy.core._print_helpers import Printable
from typing import Union

from nodimo.variable import Variable
from nodimo.group import VariableGroup
from nodimo._internal import (_show_object,
                              _remove_duplicates,
                              _obtain_dimensions)

VariableOrGroup = Union[Variable, VariableGroup]


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

    def __init__(self, *variables: VariableOrGroup):

        self.variables: VariableOrGroup = _remove_duplicates(list(variables))
        self.dimensions: list[str] = _obtain_dimensions(*variables)
    
    def show(self):
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
