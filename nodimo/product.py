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

from sympy import srepr, Mul, S
from sympy.printing.pretty.stringpict import prettyForm

from nodimo.quantity import Quantity, Constant, One
from nodimo.collection import Collection
from nodimo.power import Power
from nodimo._internal import _prettify_name


class Product(Quantity):
    """Product of quantities.

    Parameters
    ----------
    *quantities : Quantity
        Quantities to be multiplied.
    name : str, default=''
        Name (symbol) to be used as the product representation.
    dependent : bool, default=False
        If ``True``, the product is dependent.
    scaling : bool, default=False
        If ``True``, the product can be used as scaling parameter.
    reduce : bool, default=True
        If ``True``, the product is simplified or rearranged.

    Attributes
    ----------
    factors : list[Quantity]
        Multiplication factors.

    Methods
    -------
    reduce()
        Turns an unreduced quantity into a reduced quantity.

    Raises
    ------
    TypeError
        If at least one of the factors is not a quantity.

    Examples
    --------

    >>> from nodimo import Quantity, Product
    >>> a = Quantity('a', A=-2, B=1)
    >>> b = Quantity('b', A=2, B=-1)
    >>> c = Product(a, b)

    The ``*`` operator can also be used to create a product:
    
    >>> d = a*b
    """

    _is_product = True
    _is_derived = True

    def __new__(
        cls,
        *factors: Quantity,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True,
    ):
        if not all(isinstance(qty, Quantity) for qty in factors):
            raise TypeError(f"All product inputs must be quantities")
        elif reduce:
            factors = cls._simplify_factors(*factors)

        if len(factors) == 0:
            return One()
        elif len(factors) == 1:
            return factors[0]
        return super().__new__(cls)

    def __init__(
        self,
        *factors: Quantity,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True,
    ):
        self._preset_product(*factors, reduce=reduce)

        product_dimension = self._factors[0].dimension
        for qty in self._factors[1:]:
            product_dimension *= qty.dimension

        dummy_name = 'Product' if name == '' else name
        super().__init__(
            name=dummy_name, **product_dimension, dependent=dependent, scaling=scaling
        )

        self._set_product(reduce=reduce)
        self._validate_quantity()
        self._numerator_quantities: list[Quantity]
        self._denominator_quantities: list[Quantity]
        if name == '':
            self._name = name
            self._set_numerator_quantities()
            self._set_symbolic_product()

    @property
    def factors(self) -> list[Quantity]:
        return self._factors

    @classmethod
    def _simplify_factors(cls, *initial_factors: Quantity):
        col = Collection(*initial_factors)
        col._quantities = col._disassembled_quantities
        col._set_constants()
        factors: list[Quantity] = [Constant(Mul(*col._number_constants))]
        col._clear_constants(only_numbers=True)

        if len(col._quantities) > len(col._base_quantities):
            for base_qty in col._base_quantities:
                exponent = S.Zero
                for qty in col._quantities:
                    if qty == base_qty:
                        exponent += S.One
                    elif qty._is_power:
                        if qty._base == base_qty:
                            exponent += qty._exponent
                factors.append(Power(base_qty, exponent))
        else:
            factors.extend(col._quantities)

        col._quantities = factors
        col._clear_constants(only_ones=True)

        return col._quantities

    def _preset_product(self, *factors: Quantity, reduce: bool = True):
        if reduce:
            self._factors = self._simplify_factors(*factors)
        else:
            self._factors = list(factors)

    def _set_product(self, reduce: bool = True):
        if bool(reduce):
            self._is_reduced = True
        elif any(not qty._is_reduced for qty in self._factors):
            self._is_reduced = False
        else:
            reduced_factors = self._simplify_factors(*self._factors)
            if frozenset(self._factors) == frozenset(reduced_factors):
                self._is_reduced = True
            else:
                self._is_reduced = False

        if all(qty._is_constant for qty in self._factors):
            self._is_constant = True
            self._is_number = all(qty._is_number for qty in self._factors)
        else:
            if 'reduced_quantities' not in locals():
                reduced_factors = self._simplify_factors(*self._factors)
            self._is_constant = all(qty._is_constant for qty in reduced_factors)
            self._is_number = all(qty._is_number for qty in reduced_factors)

        if self._is_constant:
            self._name = _prettify_name(self._name, bold=True)
            self._set_symbolic_quantity()

    def _set_symbolic_product(self):
        """Not currently used by the printing methods.

        The symbolic attribute created here is not used for printing
        because the factors don't follow input order.
        """

        qty_symb = [qty._symbolic for qty in self._factors]
        self._symbolic = Mul(*qty_symb, evaluate=False)

    def _copy(self):
        qty_copy = eval(srepr(self))
        qty_copy._unreduced = self._unreduced
        return qty_copy

    def _key(self) -> tuple:
        return (frozenset(self.reduce()._factors),)

    def _set_numerator_quantities(self):
        numerator_quantities = []
        denominator_quantities = []
        for qty in self._factors:
            if qty._is_power and qty.exponent < 0 and not qty._name:
                qty._exponent *= -1
                qtyinv = qty._copy()
                qty._exponent *= -1
                denominator_quantities.append(qtyinv)
            else:
                numerator_quantities.append(qty)
        if len(numerator_quantities) == 0:
            numerator_quantities.append(One())

        self._numerator_quantities = numerator_quantities
        self._denominator_quantities = denominator_quantities
        self._is_quotient = bool(denominator_quantities)

    def _sympyrepr(self, printer):
        class_name = type(self).__name__
        factors = ', '.join(printer._print(qty) for qty in self._factors)
        name = f", name='{self._name}'" if self._name else ''
        dependent = f', dependent=True' if self._is_dependent else ''
        scaling = f', scaling=True' if self._is_scaling else ''
        reduce = f', reduce=False' if not self._is_reduced else ''

        return f'{class_name}({factors}{name}{dependent}{scaling}{reduce})'

    def _sympystr(self, printer):
        if self._name:
            return printer._print(self._symbolic)

        numerator_quantities = []
        for i, qty in enumerate(self._numerator_quantities):
            quantity = printer._print(qty)
            if qty._is_quotient or (i > 0 and qty._is_number and qty._symbolic < 0):
                quantity = f'({quantity})'
            numerator_quantities.append(quantity)
        numerator = '*'.join(numerator_quantities)

        if not self._is_quotient:
            return numerator

        denominator_quantities = []
        for i, qty in enumerate(self._denominator_quantities):
            quantity = printer._print(qty)
            if qty._is_quotient or (i > 0 and qty._is_number and qty._symbolic < 0):
                quantity = f'({quantity})'
            denominator_quantities.append(quantity)
        denominator = '*'.join(denominator_quantities)

        if len(self._denominator_quantities) > 1:
            denominator = f'({denominator})'
        elif len(self._denominator_quantities) == 1:
            qty = self._denominator_quantities[0]
            if qty._is_product and not qty._is_quotient:
                denominator = f'({denominator})'

        quotient = f'{numerator}/{denominator}'

        return quotient

    def _latex(self, printer):
        if self._name:
            return printer._print(self._symbolic)

        numerator_quantities = []
        for i, qty in enumerate(self._numerator_quantities):
            quantity = printer._print(qty)
            if i > 0 and (qty._is_number and qty._symbolic < 0):
                quantity = f'\\left({quantity}\\right)'
            numerator_quantities.append(quantity)
        numerator = ' '.join(numerator_quantities)

        if not self._is_quotient:
            return numerator

        denominator_quantities = []
        for i, qty in enumerate(self._denominator_quantities):
            quantity = printer._print(qty)
            if i > 0 and (qty._is_number and qty._symbolic < 0):
                quantity = f'\\left({quantity}\\right)'
            denominator_quantities.append(quantity)
        denominator = ' '.join(denominator_quantities)

        quotient = f'\\frac{{{numerator}}}{{{denominator}}}'

        return quotient

    def _pretty(self, printer):
        if self._name:
            return printer._print(self._symbolic)

        numerator = printer._print(self._numerator_quantities[0])
        for qty in self._numerator_quantities[1:]:
            quantity = printer._print(qty)
            if qty._is_number and qty._symbolic < 0:
                quantity = prettyForm(*quantity.parens())
            numerator *= quantity

        if not self._is_quotient:
            return numerator

        denominator = printer._print(self._denominator_quantities[0])
        for qty in self._denominator_quantities[1:]:
            quantity = printer._print(qty)
            if qty._is_number and qty._symbolic < 0:
                quantity = prettyForm(*quantity.parens())
            denominator *= quantity

        quotient = numerator / denominator
        # Binding is changed from DIV to ATOM to avoid parenthesis.
        quotient.binding = prettyForm.ATOM

        return quotient
