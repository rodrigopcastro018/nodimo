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

from sympy import Rational
from nodimo.variable import BasicVariable


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
        self._exponent: Rational = Rational(exponent).limit_denominator(1000)
        self._set_dimensions()
        
        self.is_dependent = dependent
        self.is_scaling = scaling

    # Removing the dimensions.setter method
    @BasicVariable.dimensions.setter
    def dimensions(self, dimensions: dict[str, int]):
        raise AttributeError(
            f"property 'dimensions' of '{type(self).__name__}' object has no setter"
        )
    
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

