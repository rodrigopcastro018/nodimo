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
    reduce : bool, default=True
        If ``True``, the product is simplified or rearranged.

    Attributes
    ----------
    quantities : tuple[Quantity]
        Multiplication factors.

    Raises
    ------
    TypeError
        If at least one of the factors is not a quantity.
    """

    _is_product = True
    _is_derived = True

    def __new__(
        cls,
        *quantities: Quantity,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True,
    ):
        if not all(isinstance(qty, Quantity) for qty in quantities):
            raise TypeError(f"All product inputs must be quantities")
        elif reduce:
            quantities = cls._simplify_factors(*quantities)

        if len(quantities) == 0:
            return One()
        elif len(quantities) == 1:
            return quantities[0]
        return super().__new__(cls)

    def __init__(
        self,
        *quantities: Quantity,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
        reduce: bool = True,
    ):
        self._preset_product(*quantities, reduce=reduce)

        product_dimension = self._quantities[0].dimension
        for qty in self._quantities[1:]:
            product_dimension *= qty.dimension

        dummy_name = 'Product' if name == '' else name
        super().__init__(
            name=dummy_name, **product_dimension, dependent=dependent, scaling=scaling,
        )

        self._set_product(reduce)
        self._validate_quantity()
        self._numerator_quantities: tuple[Quantity]
        self._denominator_quantities: tuple[Quantity]
        if name == '':
            self._name = name
            self._set_numerator_quantities()
            self._set_symbolic_product()

    @property
    def quantities(self) -> tuple[Quantity]:
        return self._quantities

    @classmethod
    def _simplify_factors(cls, *quantities: Quantity) -> tuple[Quantity]:
        col = Collection(*quantities)
        col._quantities = col._disassembled_quantities
        col._set_constants()
        quantities = [Constant(Mul(*col._number_constants))]
        col._clear_constants(only_numbers=True)

        if len(col._quantities) > len(col._base_quantities):
            for base_qty in col._base_quantities:
                exponent = S.Zero
                for qty in col._quantities:
                    if qty == base_qty:
                        exponent += S.One
                    elif qty._is_power:
                        if qty._quantity == base_qty:
                            exponent += qty._exponent
                quantities.append(Power(base_qty, exponent))
        else:
            quantities.extend(col._quantities)

        col._quantities = tuple(quantities)
        col._clear_constants(only_ones=True)

        return col._quantities

    def _preset_product(self, *quantities: Quantity, reduce: bool):
        if reduce:
            self._quantities = self._simplify_factors(*quantities)
        else:
            self._quantities = quantities

    def _set_product(self, reduce: bool):
        if bool(reduce):
            self._is_reduced = True
        elif any(not qty._is_reduced for qty in self._quantities):
            self._is_reduced = False
        else:
            reduced_factors = self._simplify_factors(*self._quantities)
            if self._quantities == reduced_factors:
                self._is_reduced = True
            else:
                self._is_reduced = False

        if all(qty._is_constant for qty in self._quantities):
            self._is_constant = True
            self._is_number = all(qty._is_number for qty in self._quantities)
        else:
            if 'reduced_quantities' not in locals():
                reduced_factors = self._simplify_factors(*self._quantities)
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

        qty_symb = []
        for qty in self._quantities:
            if qty._is_power and qty._name:
                qty_pow = Power(qty.quantity, qty.exponent)
                qty_symb.append(qty_pow._symbolic)
            else:
                qty_symb.append(qty._symbolic)
        self._symbolic = Mul(*qty_symb, evaluate=False)

    def _copy(self):
        qty_copy = eval(srepr(self))
        qty_copy._unreduced = self._unreduced
        return qty_copy

    def _key(self) -> tuple:
        return (frozenset(self._reduce()._quantities),)

    def _set_numerator_quantities(self):
        numerator_quantities = []
        denominator_quantities = []
        for qty in self._quantities:
            if qty._is_power and qty.exponent < 0 and not qty._name:
                qty._exponent *= -1
                qtyinv = qty._copy()
                qty._exponent *= -1
                denominator_quantities.append(qtyinv)
            else:
                numerator_quantities.append(qty)
        if len(numerator_quantities) == 0:
            numerator_quantities.append(One())

        self._numerator_quantities = tuple(numerator_quantities)
        self._denominator_quantities = tuple(denominator_quantities)
        self._is_quotient = bool(denominator_quantities)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantities = ', '.join(printer._print(qty) for qty in self._quantities)
        name = f", name='{self.name}'" if self.name else ''
        dependent = f', dependent=True' if self.is_dependent else ''
        scaling = f', scaling=True' if self.is_scaling else ''
        reduce = f', reduce=False' if not self._is_reduced else ''

        return f'{class_name}({quantities}{name}{dependent}{scaling}{reduce})'

    def _sympystr(self, printer) -> str:
        printer.set_global_settings(root_notation=False)

        if self._name:
            return printer._print(self._symbolic)

        numerator_quantities = []
        for qty in self._numerator_quantities:
            quantity = printer._print(qty)
            if qty._is_quotient:
                quantity = f'({quantity})'
            numerator_quantities.append(quantity)
        numerator = '*'.join(numerator_quantities)

        if not self._is_quotient:
            return numerator

        denominator_quantities = []
        for qty in self._denominator_quantities:
            quantity = printer._print(qty)
            if qty._is_quotient:
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

    def _latex(self, printer) -> str:
        printer.set_global_settings(root_notation=False)

        if self._name:
            return printer._print(self._symbolic)

        numerator_quantities = []
        for qty in self._numerator_quantities:
            numerator_quantities.append(printer._print(qty))
        numerator = ' '.join(numerator_quantities)

        if not self._is_quotient:
            return numerator

        denominator_quantities = []
        for qty in self._denominator_quantities:
            denominator_quantities.append(printer._print(qty))
        denominator = ' '.join(denominator_quantities)

        quotient = f'\\frac{{{numerator}}}{{{denominator}}}'
        
        return quotient

    def _pretty(self, printer) -> prettyForm:
        printer.set_global_settings(root_notation=False)

        if self._name:
            return printer._print(self._symbolic)

        numerator = printer._print(self._numerator_quantities[0])
        for qty in self._numerator_quantities[1:]:
            numerator *= printer._print(qty)

        if not self._is_quotient:
            return numerator

        denominator = printer._print(self._denominator_quantities[0])
        for qty in self._denominator_quantities[1:]:
            denominator *= printer._print(qty)

        quotient = numerator/denominator
        # Binding is changed from DIV to ATOM to avoid parenthesis.
        quotient.binding = prettyForm.ATOM

        return quotient
