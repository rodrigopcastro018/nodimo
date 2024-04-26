"""
=================================
Power (:mod:`nodimo.power`)
=================================

This module contains the classes to create a variable power.

Classes
-------
BasicPower
    Base class for the power of a variable.
Power
    Creates a symbolic power of a variable.
"""

from sympy import Rational, Pow
from typing import Optional

from nodimo.variable import Variable, OneVar
from nodimo._internal import _sympify_number, _repr


class Exponentiation:
    """Exponentiation operator.

    To not be confused with the class Power, which represents the
    exponentiation result. This class operates some simplifications
    on the exponentiation operator.

    Parameters
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Rational
        Exponent to which the variable will be raised.

    Attributes
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Rational
        Exponent to which the variable will be raised.
    """

    def __init__(self, variable: Variable, exponent: Rational):

        exponent_sp = _sympify_number(exponent)
        
        if isinstance(variable, Exponentiation):
            exponent_sp *= variable._exponent
            variable = variable._variable

        self._variable: Variable = variable
        self._exponent: Rational = exponent_sp

    @property
    def variable(self) -> Variable:
        return self._variable

    @property
    def exponent(self) -> Rational:
        return self._exponent


class BasicPower(Variable, Exponentiation):
    """Base class for the power of a variable.

    Base class that represents the power of a variable. The dimensional
    properties of the power are calculated from the input variable and
    the exponent.

    Parameters
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Rational
        Exponent to which the variable will be raised.
    name : Optional[str], default=None
        Name to be used in string representation.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
    name : Optional[str]
        Name to be used in string representation.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the power is dependent.
    is_scaling : bool
        If ``True``, the power can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the power is nondimensional.

    Raises
    ------
    ValueError
        If the power is set as both dependent and scaling.
    ValueError
        If the power is set as scaling when it has no dimensions.
    """

    def __new__(
        cls,
        variable: Variable,
        exponent: Rational,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False,
    ):
        
        exponent_sp = _sympify_number(exponent)

        if exponent_sp == 0:
            return OneVar()
        elif exponent_sp == 1:
            if isinstance(variable, BasicPower):
                return super().__new__(cls)
            return variable
        else:
            return super().__new__(cls)

    def __init__(
        self,
        variable: Variable,
        exponent: Rational,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False,
    ):

        super().__init__(name=name)
        Exponentiation.__init__(self, variable, exponent)
        self._set_dimensions()
        self.is_dependent = dependent
        self.is_scaling = scaling

    # Redefining dimensions as a read-only property
    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    # def combine(self, name: Optional[str] = None) -> BasicCombinedVariable:
    #     """Converts to a combined variable."""

    #     return BasicCombinedVariable(self, name)

    def _set_dimensions(self):
        """Evaluates the dimensions of the power."""

        if self._variable.is_nondimensional:
            pass
        else:
            dimensions = {}
            for dim, exp in self._variable.dimensions.items():
                dimensions[dim] = exp * self._exponent
            
            self._dimensions = dimensions
            self._is_nondimensional = all(dim == 0 for dim in self._dimensions.values())

    def __str__(self) -> str:
        
        if self.name is not None:
            return self.name
        else:
            return f'{self._variable.name}**{self._exponent}'  # TODO: Add parenthesis for negative and rationals.

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variable_repr = _repr(self._variable)
        exponent_repr = f', {_repr(self._exponent)}'
        name_repr = f", name='{self.name}'" if self.name else ''
        dependent_repr = f', dependent=True' if self.is_dependent else ''
        scaling_repr = f', scaling=True' if self.is_scaling else ''

        return (f'{class_name}('
                + variable_repr
                + exponent_repr
                + name_repr
                + dependent_repr
                + scaling_repr
                + ')')


class Power(Pow, BasicPower):
    """Creates a symbolic power of a variable.

    This class inherits the dimensional properties of BasicPower and
    adds to it, by inheriting from sympy.Power, the ability to be used
    in symbolic mathematical expressions.

    Parameters
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Rational
        Exponent to which the variable will be raised.
    name : Optional[str], default=None
        The name that will be displayed in symbolic expressions.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
    name : Optional[str]
        The name that will be displayed in symbolic expressions.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the power is dependent.
    is_scaling : bool
        If ``True``, the power can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the power is nondimensional.

    Raises
    ------
    ValueError
        If the power is set as both dependent and scaling.
    ValueError
        If the power is set as scaling when it has no dimensions.
    """

    def __new__(
        cls,
        variable: Variable,
        exponent: Rational,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False
    ):

        exponent_sp = _sympify_number(exponent)

        if exponent_sp == 0:
            return OneVar()
        else:
            return super().__new__(cls, variable, exponent_sp)

    def __init__(
        self,
        variable: Variable,
        exponent: Rational,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False
    ):

        super().__init__(variable, exponent, name=name, dependent=dependent, scaling=scaling)

    # def combine(self, name: Optional[str] = None) -> CombinedVariable:
    #     """Converts to a combined variable."""

    #     return CombinedVariable(self, name)

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        if self.name:
            return printer._print_Symbol(self)
        else:
            return printer._print_Pow(self)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        return BasicPower.__repr__(self)

    _latex = _pretty = _sympystr