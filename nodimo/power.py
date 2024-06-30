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

from sympy import srepr, Symbol, Pow, Number, S, Abs
from sympy.printing.pretty.stringpict import prettyForm

from nodimo.quantity import Quantity, Constant, One
from nodimo._internal import _sympify_number, _unsympify_number, _prettify_name


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
    reduce : bool, default=True
        If ``True``, the exponentiation is simmplified.

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
    _is_derived = True

    def __new__(
        cls,
        quantity: Quantity,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True
    ):
        if not isinstance(quantity, Quantity):
            raise TypeError(f"{repr(quantity)} is not a quantity")
        elif quantity._is_one:
            return One()
        exponent_sp = _sympify_number(exponent)
        if exponent_sp == 0:
            return One()

        if reduce:
            if quantity._is_power:
                exponent_sp *= quantity._exponent
                quantity = quantity._quantity
            if quantity._is_number:
                return Constant(quantity._symbolic**exponent_sp)
            if quantity._is_product:
                from nodimo.product import Product
                factors = []
                for qty in quantity.quantities:
                    factors.append(Power(qty, exponent_sp))
                return Product(
                    *factors, name=name, dependent=dependent, scaling=scaling
                )

        if exponent_sp == 1:
            return quantity

        return super().__new__(cls)

    def __init__(
        self,
        quantity: Quantity,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True
    ):
        self._quantity: Quantity
        self._exponent: Number
        self._preset_power(quantity, exponent, reduce)
        power_dimension = self._quantity.dimension**self._exponent
        dummy_name = 'Power' if name == '' else name
        super().__init__(
            dummy_name, **power_dimension, dependent=dependent, scaling=scaling,
        )
        self._set_power(reduce)
        self._validate_quantity()
        if name == '':
            self._name = name
            self._set_symbolic_power()

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def exponent(self) -> Number:
        return self._exponent

    def _preset_power(self, quantity: Quantity, exponent: Number, reduce: bool):
        exponent_sp = _sympify_number(exponent)
        if reduce and quantity._is_power:
            exponent_sp *= quantity.exponent
            quantity = quantity.quantity

        self._quantity = quantity
        self._exponent = exponent_sp

    def _set_power(self, reduce: bool):
        self._is_constant = self._quantity._is_constant
        self._is_number = self._quantity._is_number
        self._is_reduced = bool(reduce)
        if not self._quantity._is_derived and not self._is_number:
            self._is_reduced = True
        if self._quantity._is_quotient or self._exponent < 0:
            self._is_quotient = True
        if self._is_constant:
            self._name = _prettify_name(self._name, bold=True)
            self._set_symbolic_quantity()

    def _set_symbolic_power(self):
        """Not currently used by the printing methods.

        The symbolic attribute created here is not used for printing
        because unevaluated powers of numbers can not always be printed.
        """

        self._symbolic = Pow(self._quantity._symbolic, self._exponent, evaluate=False)
        if self._is_number:
            self._symbolic = self._symbolic.doit()

    def _copy(self):
        if self._quantity._is_product:
            from nodimo.product import Product
        qty_copy = eval(srepr(self))
        qty_copy._unreduced = self._unreduced
        return qty_copy

    def _key(self) -> tuple:
        return (self._quantity._reduce(), self._exponent)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantity = printer._print(self._quantity)
        unsymp_exp = _unsympify_number(self._exponent)
        exponent = f', {repr(unsymp_exp)}'
        name = f", name='{self.name}'" if self.name else ''
        dependent = f', dependent=True' if self.is_dependent else ''
        scaling = f', scaling=True' if self.is_scaling else ''
        reduce = f', reduce=False' if not self._is_reduced else ''

        return f'{class_name}({quantity}{exponent}{name}{dependent}{scaling}{reduce})'

    def _sympystr(self, printer) -> str:
        printer._settings['root_notation'] = False

        if self._name:
            return printer._print(self._symbolic)

        pb = self._quantity
        bs = pb._symbolic
        pe = Abs(self._exponent)

        if bs.is_Symbol or bs.is_NumberSymbol:
            base = printer._print(pb)
        elif (bs.is_Integer or bs.is_Float) and bs > 0:
            base = printer._print(pb)
        elif bs.is_Pow and bs.exp is S.Half:
            base = printer._print(pb)
        else:
            base = f'({printer._print(pb)})'
        
        if pe.is_Integer or pe.is_Float or pe.is_NumberSymbol:
            exponent = printer._print(pe)
        elif pe.is_Pow and pe.exp is S.Half:
            exponent = printer._print(pe)
        else:
            exponent = f'({printer._print(pe)})'

        if pe == 1:
            power = base
        else:
            power = f'{base}**{exponent}'

        if self._exponent > 0:
            return power
        else:
            return f'{1}/{power}'

    def _latex(self, printer) -> str:
        printer._settings['root_notation'] = False

        if self._name:
            return printer._print(self._symbolic)

        pb = self._quantity
        bs = pb._symbolic
        pe = Abs(self._exponent)

        if bs.is_Symbol or bs.is_NumberSymbol or pe == 1:
            base = printer._print(pb)
        elif (bs.is_Integer or bs.is_Float) and bs > 0:
            base = printer._print(pb)
        elif bs.is_Pow and bs.exp is S.Half:
            base = printer._print(pb)
        else:
            base = f'\\left({printer._print(pb)}\\right)'
        
        printer._settings['root_notation'] = True
        if pe == 1:
            power = base
        else:
            exponent = printer._print(pe)
            power = f'{{{base}}}^{{{exponent}}}'

        if self._exponent > 0:
            return power
        else:
            return f'\\frac{{{1}}}{{{power}}}'

    def _pretty(self, printer) -> prettyForm:
        printer._settings['root_notation'] = False

        if self._name:
            return printer._print(self._symbolic)

        pb = self._quantity
        bs = pb._symbolic
        pe = Abs(self._exponent)

        if bs.is_Symbol or bs.is_NumberSymbol or pe == 1:
            base = printer._print(pb)
            # Binding is fixed to ATOM to avoid parenthesis.
            base.binding = prettyForm.ATOM
        elif (bs.is_Integer or bs.is_Float) and bs > 0:
            base = printer._print(pb)
        elif bs.is_Pow and bs.exp is S.Half:
            base = printer._print(pb)
        else:
            base = prettyForm(*printer._print(pb).parens())
        
        printer._settings['root_notation'] = True
        if pe == 1:
            power = base
        else:
            exponent = printer._print(pe)
            power = base**exponent

        if self._exponent > 0:
            return power
        else:
            return printer._print(S.One)/power
