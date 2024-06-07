#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Product
=======

This module contains the class to create the product of quantities.

Classes
-------
Product
    Creates the product of quantities.
"""

from sympy import srepr, Symbol, Pow, Mul, S
from functools import reduce
from typing import Union

from nodimo.quantity import Quantity, One
from nodimo.collection import Collection
from nodimo.power import Power


class Product(Quantity):
    """Product of quantities.

    This class represents the product of quantities.

    Parameters
    ----------
    *quantities : Quantity
        Quantities to be multiplied.
    name : str, default=''
        Name to be used as the product representation.
    dependent : bool, default=False
        If ``True``, the product is dependent.
    scaling : bool, default=False
        If ``True``, the product can be used as scaling parameter.

    Attributes
    ----------
    quantities : tuple[Quantity]
        Multiplication factors.
    """

    _is_product = True

    def __new__(
        cls,
        *quantities: Quantity,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        simplified_quantities = cls._simplify_factors(*quantities)

        if len(simplified_quantities) == 0:
            return One()
        if len(simplified_quantities) == 1:
            return simplified_quantities[0]
        else:
            return super().__new__(cls)

    def __init__(
        self,
        *quantities: Quantity,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        self._quantities = self._simplify_factors(*quantities)
        product_dimension = reduce(
            lambda x, y: x*y, (qty.dimension for qty in self._quantities)
        )
        dummy_name = 'Product' if name == '' else name
        super().__init__(
            name=dummy_name, **product_dimension, dependent=dependent, scaling=scaling,
        )
        self._numerator_symbols: tuple[Union[Symbol, Mul, Pow]]
        self._denominator_symbols: tuple[Union[Symbol, Mul, Pow]]
        if name == '':
            self._name = name
            self._set_numerator_symbols()
            self._set_symbolic_product()

    @property
    def quantities(self) -> tuple[Quantity]:
        return self._quantities

    @classmethod
    def _simplify_factors(self, *quantities: Quantity) -> tuple[Quantity]:
        col = Collection(*quantities)
        col._set_base_quantities()
        col._quantities = col._disassembled_quantities
        col._clear_ones()

        if len(col._quantities) > len(col._base_quantities):
            quantities = []
            for base_qty in col._base_quantities:
                exponent = S.Zero
                for qty in col._quantities:
                    if qty == base_qty:
                        exponent += S.One
                    elif qty._is_power:
                        if qty._quantity == base_qty:
                            exponent += qty._exponent
                quantities.append(Power(base_qty, exponent))
            col._quantities = tuple(quantities)
            col._clear_ones()

        return col._quantities

    def _set_symbolic_product(self):
        """Not currently used by the printing methods.

        The symbolic attribute created here is not used for printing
        because the denominator symbols don't follow input order.
        """

        qty_symb = []
        for qty in self._quantities:
            if qty._is_power and qty._name:
                qty_pow = Power(qty.quantity, qty.exponent)
                qty_symb.append(qty_pow._symbolic)
            else:
                qty_symb.append(qty._symbolic)
        self._symbolic = Mul(*qty_symb)

    def _copy(self):
        return eval(srepr(self))

    def _key(self) -> tuple:
        return (frozenset(self._quantities),)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantities = ', '.join(printer._print(qty) for qty in self._quantities)
        name = f", name='{self.name}'" if self.name else ''
        dependent = f', dependent=True' if self.is_dependent else ''
        scaling = f', scaling=True' if self.is_scaling else ''

        return f'{class_name}({quantities}{name}{dependent}{scaling})'

    def _set_numerator_symbols(self):
        numerator_symbols = []
        denominator_symbols = []
        for qty in self._quantities:
            if qty._is_power and qty.exponent < 0:
                qtyinv = Power(qty.quantity, -qty.exponent)
                denominator_symbols.append(qtyinv._symbolic)
            else:
                if qty._is_power and qty.name:
                    qty_pow = Power(qty.quantity, qty.exponent)
                    symbol = qty_pow._symbolic
                else:
                    symbol = qty._symbolic
                numerator_symbols.append(symbol)

        self._numerator_symbols = tuple(numerator_symbols)
        self._denominator_symbols = tuple(denominator_symbols)

    def _printmethod(self, printer):
        """Keeps the input order on output representations."""

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.

        if self._name:
            return printer._print(self._symbolic)

        numerator = printer._print(Mul(*self._numerator_symbols))

        if len(self._denominator_symbols) > 0:
            denominator = printer._print(Mul(*self._denominator_symbols))
            if printer.printmethod == '_sympystr':
                return f'{numerator}/({denominator})'
            elif printer.printmethod == '_pretty':
                return numerator / denominator
            elif printer.printmethod == '_latex':
                return f'\\frac{{{numerator}}}{{{denominator}}}'
        else:
            return numerator

    _latex = _pretty = _sympystr = _printmethod

        
Prod = Product
