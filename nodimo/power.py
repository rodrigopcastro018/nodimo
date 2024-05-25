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

from sympy import srepr, Symbol, Pow, Number, S
from typing import Optional

from nodimo.variable import Variable, OneVar
from nodimo._internal import _sympify_number, _unsympify_number


class Power(Variable):
    """Base class for the power of a variable.

    Base class that represents the power of a variable. The dimensional
    properties of the power are calculated from the input variable and
    the exponent.

    Parameters
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Number
        Exponent to which the variable will be raised.

    Attributes
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Number
        Exponent to which the variable will be raised.
    """

    _is_power = True

    def __new__(
        cls,
        variable: Variable,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        if isinstance(variable, OneVar):
            return OneVar()

        exponent_sp = _sympify_number(exponent)
        if isinstance(variable, Power):
            exponent_sp *= variable._exponent
            variable = variable._variable

        if exponent_sp == 0:
            return OneVar()
        elif exponent_sp == 1:
            if variable.symbolic.is_commutative:
                variable._set_symbolic_variable()
            return variable
        
        if variable._is_product:
            from nodimo.product import Product
            factors = []
            for var in variable.variables:
                factors.append(Power(var, exponent_sp))
            
            return Product(*factors, name=name, dependent=dependent, scaling=scaling)

        return super().__new__(cls)

    def __init__(
        self,
        variable: Variable,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        exponent_sp = _sympify_number(exponent)
        if isinstance(variable, Power):
            exponent_sp *= variable._exponent
            variable = variable._variable

        self._variable: Variable = variable
        self._exponent: Number = exponent_sp
        self._set_power_dimensions()

        dummy_name = 'Power' if name == '' else name
        super().__init__(
            name=dummy_name, **self._dimensions, dependent=dependent, scaling=scaling,
        )

        if name == '':
            self._name = name
            self._set_symbolic_power()

    @property
    def variable(self) -> Variable:
        return self._variable

    @property
    def exponent(self) -> Number:
        return self._exponent

    def _set_power_dimensions(self):
        dimensions = {}
        if not self._variable.is_nondimensional:
            for dim, exp in self._variable.dimensions.items():
                dimensions[dim] = exp * self._exponent

        self._dimensions = dimensions
    
    def _set_symbolic_power(self):
        var = self._variable
        # Setting com=True avoids variables with negative exponents on
        # the numerator in Product.symbolic.
        com = True if self._exponent < S.Zero else False
        self._variable._symbolic = Symbol(var.name, commutative=com)
        self._symbolic = Pow(self._variable.symbolic, self._exponent)

    def _copy(self):
        return eval(srepr(self))

    def _key(self) -> tuple:
        return (self._variable, self._exponent)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variable_repr = printer._print(self._variable)

        unsymp_exp = _unsympify_number(self._exponent)
        exp_ = f"'{unsymp_exp}'" if isinstance(unsymp_exp, str) else unsymp_exp
        exponent_repr = f', {exp_}'

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
