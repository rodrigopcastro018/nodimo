#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Power
=====

This module contains the class to create a power of a variable.

Classes
-------
Power
    Creates a power of a variable.
"""

from sympy import srepr, Symbol, Pow, Number, S

from nodimo.variable import Variable, OneVar
from nodimo._internal import _sympify_number, _unsympify_number


class Power(Variable):
    """Power of a variable.

    This class represents the power of a variable.

    Parameters
    ----------
    variable : Variable
        Variable to be exponentiated.
    exponent : Number
        Exponent to which the variable will be raised.
    name : str, default=''
        Name to be used as the power representation.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
    variable : Variable
        Variable that is the base of the exponentiation.
    exponent : Number
        Exponent to which the variable is raised.
    
    Raises
    ------
    TypeError
        If the exponentiation base is not a variable.
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
            if variable._symbolic.is_commutative:
                variable._set_symbolic_variable()
            return variable
        
        if hasattr(variable, '_is_product') and variable._is_product:
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
        self._variable: Variable
        self._exponent: Number
        self._set_power(variable, exponent)
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

    def _set_power(self, variable: Variable, exponent: Number):
        if not isinstance(variable, Variable):
            raise TypeError(f"{repr(variable)} is not a variable")

        exponent_sp = _sympify_number(exponent)

        if isinstance(variable, Power):
            exponent_sp *= variable.exponent
            variable = variable.variable

        self._variable = variable
        self._exponent = exponent_sp

    def _set_power_dimensions(self):
        dimensions = {}
        if not self._variable.is_nondimensional:
            for dim, exp in self._variable.dimensions.items():
                dimensions[dim] = exp * self._exponent

        self._dimensions = dimensions

    def _set_symbolic_power(self):
        var = self._variable
        # Setting com=True avoids variables with negative exponents on
        # the numerator of Product._symbolic.
        com = True if self._exponent < S.Zero else False
        self._variable._symbolic = Symbol(var.name, commutative=com)
        self._symbolic = Pow(self._variable._symbolic, self._exponent)

    def _copy(self):
        return eval(srepr(self))

    def _key(self) -> tuple:
        return (self._variable, self._exponent)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variable = printer._print(self._variable)
        unsymp_exp = _unsympify_number(self._exponent)
        exponent = f', {repr(unsymp_exp)}'
        name = f", name='{self.name}'" if self.name else ''
        dependent = f', dependent=True' if self.is_dependent else ''
        scaling = f', scaling=True' if self.is_scaling else ''

        return f'{class_name}({variable}{exponent}{name}{dependent}{scaling})'
