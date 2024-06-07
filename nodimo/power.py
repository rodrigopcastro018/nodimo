#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Power
=====

This module contains the class to create the power of a quantity.

Classes
-------
Power
    Creates the power of a quantity.
"""

from sympy import srepr, Symbol, Pow, Number, S

from nodimo.quantity import Quantity, One
from nodimo._internal import _sympify_number, _unsympify_number


class Power(Quantity):
    """Power of a quantity.

    This class represents the power of a quantity.

    Parameters
    ----------
    quantity : Quantity
        Quantity to be exponentiated.
    exponent : Number
        Exponent to which the quantity will be raised.
    name : str, default=''
        Name to be used as the power representation.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
    quantity : Quantity
        Quantity that is the base of the exponentiation.
    exponent : Number
        Exponent to which the quantity is raised.
    
    Raises
    ------
    TypeError
        If the exponentiation base is not a quantity.
    """

    _is_power = True

    def __new__(
        cls,
        quantity: Quantity,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        if isinstance(quantity, One):
            return One()

        exponent_sp = _sympify_number(exponent)
        if isinstance(quantity, Power):
            exponent_sp *= quantity._exponent
            quantity = quantity._quantity

        if exponent_sp == 0:
            return One()
        elif exponent_sp == 1:
            if quantity._symbolic.is_commutative:
                quantity._set_symbolic_quantity()
            return quantity

        if hasattr(quantity, '_is_product') and quantity._is_product:
            from nodimo.product import Product
            factors = []
            for qty in quantity.quantities:
                factors.append(Power(qty, exponent_sp))
            
            return Product(*factors, name=name, dependent=dependent, scaling=scaling)

        return super().__new__(cls)

    def __init__(
        self,
        quantity: Quantity,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        self._quantity: Quantity
        self._exponent: Number
        self._set_power(quantity, exponent)
        power_dimension = self._quantity.dimension**self._exponent
        dummy_name = 'Power' if name == '' else name
        super().__init__(
            name=dummy_name, **power_dimension, dependent=dependent, scaling=scaling,
        )
        if name == '':
            self._name = name
            self._set_symbolic_power()

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def exponent(self) -> Number:
        return self._exponent

    def _set_power(self, quantity: Quantity, exponent: Number):
        if not isinstance(quantity, Quantity):
            raise TypeError(f"{repr(quantity)} is not a quantity")

        exponent_sp = _sympify_number(exponent)

        if isinstance(quantity, Power):
            exponent_sp *= quantity.exponent
            quantity = quantity.quantity

        self._quantity = quantity
        self._exponent = exponent_sp

    def _set_symbolic_power(self):
        qty = self._quantity
        # Setting com=True avoids quantities with negative exponents on
        # the numerator of Product._symbolic.
        com = True if self._exponent < S.Zero else False
        self._quantity._symbolic = Symbol(qty.name, commutative=com)
        self._symbolic = Pow(self._quantity._symbolic, self._exponent)

    def _copy(self):
        return eval(srepr(self))

    def _key(self) -> tuple:
        return (self._quantity, self._exponent)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantity = printer._print(self._quantity)
        unsymp_exp = _unsympify_number(self._exponent)
        exponent = f', {repr(unsymp_exp)}'
        name = f", name='{self.name}'" if self.name else ''
        dependent = f', dependent=True' if self.is_dependent else ''
        scaling = f', scaling=True' if self.is_scaling else ''

        return f'{class_name}({quantity}{exponent}{name}{dependent}{scaling})'

    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy.
        
        Rational=True is set to avoid the 'sqrt' operator on the string
        representation.
        """

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.

        return printer._print_Pow(self._symbolic, rational=True)
