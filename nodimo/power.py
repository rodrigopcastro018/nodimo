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

from sympy import Rational, Pow, srepr

from nodimo.variable import BasicVariable
from nodimo._internal import _sympify_number


class BasicPower(BasicVariable):
    """Base class for the power of a variable.

    Base class that represents the power of a variable. The dimensional
    properties of the power are calculated from the input variable and
    the exponent.

    Parameters
    ----------
    variable : BasicVariable
        Variables that compose the power.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
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

    def __init__(
        self,
        variable: BasicVariable,
        exponent: Rational,
        dependent: bool = False,
        scaling: bool = False
    ):

        super().__init__()
        self._variable: BasicVariable = variable
        self._exponent: Rational = _sympify_number(exponent)
        self._set_dimensions()
        
        self.is_dependent = dependent
        self.is_scaling = scaling

    # Redefining dimensions as a read-only property
    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions
    
    def _set_dimensions(self):
        """Evaluates the dimensions of the power."""

        if self._variable.is_nondimensional or self._exponent == 0:
            pass
        else:
            dimensions = {}
            for dim, exp in self._variable.dimensions.items():
                dimensions[dim] = exp * self._exponent
            
            self._dimensions = dimensions
            self._is_nondimensional = all(dim == 0 for dim in self._dimensions.values())


class Power(BasicPower, Pow):
    """Creates a symbolic power of a variable.

    This class inherits the dimensional properties of BasicPower and
    adds to it, by inheriting from sympy.Power, the ability to be used
    in symbolic mathematical expressions.

    Parameters
    ----------
    variable : BasicVariable
        Variables that compose the power.
    exponent : Rational
        Exponent to which the variable will be raised.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
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
        variable: BasicVariable,
        exponent: Rational,
        dependent: bool = False,
        scaling: bool = False
    ):

        return Pow.__new__(cls, variable, _sympify_number(exponent))

    def __init__(
        self,
        variable: BasicVariable,
        exponent: Rational,
        dependent: bool = False,
        scaling: bool = False
    ):

        super().__init__(variable, exponent, dependent=dependent, scaling=scaling)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variable_repr = srepr(self._variable)
        exponent_repr = f', {srepr(self._exponent)}'
        dependent_repr = f', dependent=True' if self.is_dependent else ''
        scaling_repr = f', scaling=True' if self.is_scaling else ''

        return (f'{class_name}('
                + variable_repr
                + exponent_repr
                + dependent_repr
                + scaling_repr
                + ')')
