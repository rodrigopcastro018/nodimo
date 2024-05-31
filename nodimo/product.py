#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Product
=======

This module contains the class to create a product of variables.

Classes
-------
Product
    Creates a product of variables.
"""

from sympy import srepr, Symbol, Pow, Mul, S
from functools import reduce
from typing import Union

from nodimo.variable import Variable, OneVar
from nodimo.collection import Collection
from nodimo.power import Power


class Product(Variable):
    """Product of variables.

    This class represents the product of variables.

    Parameters
    ----------
    *variables : Variable
        Variables to be multiplied.
    name : str, default=''
        Name to be used as the product representation.
    dependent : bool, default=False
        If ``True``, the product is dependent.
    scaling : bool, default=False
        If ``True``, the product can be used as scaling parameter.

    Attributes
    ----------
    variables : tuple[Variable]
        Product factors.
    """

    _is_product = True

    def __new__(
        cls,
        *variables: Variable,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        simplified_variables = cls._simplify_factors(*variables)

        if len(simplified_variables) == 0:
            return OneVar()
        if len(simplified_variables) == 1:
            return simplified_variables[0]
        else:
            return super().__new__(cls)

    def __init__(
        self,
        *variables: Variable,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        self._variables = self._simplify_factors(*variables)
        self._dimension = reduce(
            lambda x, y: x*y, (qty.dimension for qty in self._variables)
        )
        dummy_name = 'Product' if name == '' else name
        super().__init__(
            name=dummy_name, **self._dimension, dependent=dependent, scaling=scaling,
        )
        self._numerator_symbols: tuple[Union[Symbol, Mul, Pow]]
        self._denominator_symbols: tuple[Union[Symbol, Mul, Pow]]
        if name == '':
            self._name = name
            self._set_numerator_symbols()
            self._set_symbolic_product()

    @property
    def variables(self) -> tuple[Variable]:
        return self._variables

    @classmethod
    def _simplify_factors(self, *variables: Variable) -> tuple[Variable]:
        col = Collection(*variables)
        col._set_base_variables()
        col._variables = col._disassembled_variables
        col._clear_ones()

        if len(col._variables) > len(col._base_variables):
            variables = []
            for base_var in col._base_variables:
                exponent = S.Zero
                for var in col._variables:
                    if var == base_var:
                        exponent += S.One
                    elif var._is_power:
                        if var._variable == base_var:
                            exponent += var._exponent
                variables.append(Power(base_var, exponent))
            col._variables = tuple(variables)
            col._clear_ones()

        return col._variables

    def _set_symbolic_product(self):
        """Not currently used by the printing methods.

        The symbolic attribute created here is not used for printing
        because the denominator variables don't follow input order.
        """

        var_symb = []
        for var in self._variables:
            if var._is_power and var._name:
                var_pow = Power(var.variable, var.exponent)
                var_symb.append(var_pow._symbolic)
            else:
                var_symb.append(var._symbolic)
        self._symbolic = Mul(*var_symb)

    def _copy(self):
        return eval(srepr(self))

    def _key(self) -> tuple:
        return (frozenset(self._variables),)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variables = ', '.join(printer._print(var) for var in self._variables)
        name = f", name='{self.name}'" if self.name else ''
        dependent = f', dependent=True' if self.is_dependent else ''
        scaling = f', scaling=True' if self.is_scaling else ''

        return f'{class_name}({variables}{name}{dependent}{scaling})'

    def _set_numerator_symbols(self):
        numerator_symbols = []
        denominator_symbols = []
        for var in self._variables:
            if var._is_power and var.exponent < 0:
                varinv = Power(var.variable, -var.exponent)
                denominator_symbols.append(varinv._symbolic)
            else:
                if var._is_power and var.name:
                    var_pow = Power(var.variable, var.exponent)
                    symbol = var_pow._symbolic
                else:
                    symbol = var._symbolic
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
