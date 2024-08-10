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

from sympy import srepr, Pow, Number, S, Abs
from sympy.printing.pretty.stringpict import prettyForm

from nodimo.quantity import Quantity, Constant, One
from nodimo._internal import _sympify_number, _unsympify_number, _prettify_name


class Power(Quantity):
    """Power of a quantity.

    Parameters
    ----------
    base : Quantity
        Quantity to be exponentiated.
    exponent : Number
        Exponent to which the quantity will be raised.
    name : str, default=''
        Name (symbol) to be used as the power representation.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.
    reduce : bool, default=True
        If ``True``, the exponentiation is simmplified.

    Attributes
    ----------
    base : Quantity
        Quantity that is the base of the exponentiation.
    exponent : Number
        Exponent to which the quantity is raised.

    Methods
    -------
    reduce()
        Turns an unreduced quantity into a reduced quantity.

    Raises
    ------
    TypeError
        If the exponentiation base is not a quantity.
    """

    _is_power = True
    _is_derived = True

    def __new__(
        cls,
        base: Quantity,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True,
    ):
        if not isinstance(base, Quantity):
            raise TypeError(f"{repr(base)} is not a quantity")
        elif base._is_one:
            return One()
        exponent_sp = _sympify_number(exponent)
        if exponent_sp == 0:
            return One()

        if reduce:
            if base._is_power:
                exponent_sp *= base._exponent
                base = base._base
            if base._is_number:
                return Constant(Pow(base._symbolic, exponent_sp))
            if base._is_product:
                from nodimo.product import Product

                factors = []
                for qty in base._factors:
                    factors.append(Power(qty, exponent_sp))
                return Product(
                    *factors, name=name, dependent=dependent, scaling=scaling
                )

        if exponent_sp == 1:
            return base

        return super().__new__(cls)

    def __init__(
        self,
        base: Quantity,
        exponent: Number,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True,
    ):
        self._preset_power(base, exponent, reduce)
        power_dimension = self._base.dimension**self._exponent
        dummy_name = 'Power' if name == '' else name
        super().__init__(
            dummy_name, **power_dimension, dependent=dependent, scaling=scaling
        )
        self._set_power(reduce)
        self._validate_quantity()
        if name == '':
            self._name = name
            self._set_symbolic_power()

    @property
    def base(self) -> Quantity:
        return self._base

    @property
    def exponent(self) -> Number:
        return self._exponent

    def _preset_power(self, base: Quantity, exponent: Number, reduce: bool):
        exponent_sp = _sympify_number(exponent)
        if reduce and base._is_power:
            exponent_sp *= base._exponent
            base = base._base

        self._base = base
        self._exponent = exponent_sp

    def _set_power(self, reduce: bool):
        self._is_constant = self._base._is_constant
        self._is_number = self._base._is_number
        self._is_reduced = bool(reduce)
        if not self._base._is_derived and not self._is_number:
            self._is_reduced = True
        if self._base._is_quotient or self._exponent < 0:
            self._is_quotient = True
        if self._is_constant:
            self._name = _prettify_name(self._name, bold=True)
            self._set_symbolic_quantity()

    def _set_symbolic_power(self):
        """Not currently used by the printing methods.

        The symbolic attribute created here is not used for printing
        because unevaluated powers of numbers can not always be printed.
        """

        self._symbolic = Pow(self._base._symbolic, self._exponent, evaluate=False)
        if self._is_number:
            self._symbolic = self._symbolic.doit()

    def _copy(self):
        if self._base._is_product:
            from nodimo.product import Product
        qty_copy = eval(srepr(self))
        qty_copy._unreduced = self._unreduced
        return qty_copy

    def _key(self) -> tuple:
        return (self._base.reduce(), self._exponent)

    def _sympyrepr(self, printer):
        class_name = type(self).__name__
        base = printer._print(self._base)
        unsymp_exp = _unsympify_number(self._exponent)
        exponent = f', {repr(unsymp_exp)}'
        name = f", name='{self._name}'" if self._name else ''
        dependent = f', dependent=True' if self._is_dependent else ''
        scaling = f', scaling=True' if self._is_scaling else ''
        reduce = f', reduce=False' if not self._is_reduced else ''

        return f'{class_name}({base}{exponent}{name}{dependent}{scaling}{reduce})'

    def _sympystr(self, printer):
        printer._settings['root_notation'] = False

        if self._name:
            return printer._print(self._symbolic)

        pb = self._base
        bs = pb._symbolic
        pe = Abs(self._exponent)

        if bs.is_Symbol or bs.is_NumberSymbol:
            base = printer._print(pb)
        elif (bs.is_Integer or bs.is_Float) and bs > 0:
            base = printer._print(pb)
        else:
            base = f'({printer._print(pb)})'

        if pe.is_Integer or pe.is_Float or pe.is_NumberSymbol:
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

    def _latex(self, printer):
        printer._settings['root_notation'] = False

        if self._name:
            return printer._print(self._symbolic)

        pb = self._base
        bs = pb._symbolic
        pe = Abs(self._exponent)

        if bs.is_Symbol or bs.is_NumberSymbol or pe == 1:
            base = printer._print(pb)
        elif (bs.is_Integer or bs.is_Float) and bs > 0:
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

    def _pretty(self, printer):
        printer._settings['root_notation'] = False

        if self._name:
            return printer._print(self._symbolic)

        pb = self._base
        bs = pb._symbolic
        pe = Abs(self._exponent)

        if bs.is_Symbol or bs.is_NumberSymbol or pe == 1:
            base = printer._print(pb)
            # Binding is fixed to ATOM to avoid parenthesis.
            base.binding = prettyForm.ATOM
        elif (bs.is_Integer or bs.is_Float) and bs > 0:
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
            return printer._print(S.One) / power
