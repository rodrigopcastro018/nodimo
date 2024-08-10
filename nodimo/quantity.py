#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Quantity
========

This module contains the class to create a physical quantity.

Classes
-------
Quantity
    Creates a quantity.
Constant
    Creates a dimensionless constant.
One
    Creates a dimensionless number one.
"""

from sympy import sstr, srepr, latex, Symbol, Mul, Pow, Number
from typing import Optional, Union

from nodimo.dimension import Dimension
from nodimo._internal import _sympify_number, _unsympify_number, _prettify_name


class Quantity:
    """Base class for quantities.

    Most basic type of physical quantity, with attributes that are
    useful in describing its dimensional properties.

    Parameters
    ----------
    name : str
        Name (symbol) to be used as the quantity representation.
    dependent : bool, default=False
        If ``True``, the quantity is considered dependent in a relation
        of quantities
    scaling : bool, default=False
        If ``True``, the quantity can be used as scaling parameter.
    **dimensions : Number
        The dimensions of the quantity given as keyword arguments.

    Attributes
    ----------
    name : str
        Name (symbol) used as the quantity representation.
    dimension : Dimension
        The quantity dimension.
    is_dependent : bool
        If ``True``, the quantity is considered dependent in a relation.
        of quantities
    is_scaling : bool
        If ``True``, the quantity can be used as scaling parameter.
    is_dimensionless : bool
        If ``True``, the quantity is dimensionless.

    Methods
    -------
    reduce()
        Turns an unreduced quantity into a reduced quantity.

    Raises
    ------
    TypeError
        If the quantity name is not a string.
    ValueError
        If the quantity name is invalid.
    ValueError
        If the quantity is set as both dependent and scaling.
    ValueError
        If the quantity is set as scaling, but with no dimensions.

    Examples
    --------
    Considering the dimensions mass ``M``, length ``L`` and time ``T``,
    a force ``F`` can be defined as:

    >>> from nodimo import Quantity
    >>> F = Quantity('F', M=1, L=1, T=-2)

    To define a dimensionless quantity ``A`` is sufficient to provide
    just its name:

    >>> A = Quantity('A')

    To use a greek letter in symbolic expressions, just provide its
    english representation as the name of the quantity:

    >>> a = Quantity('alpha')
    """

    _is_power: bool = False
    _is_product: bool = False
    _is_derived: bool = False
    _is_one: bool = False

    def __init__(
        self,
        name: str,
        dependent: bool = False,
        scaling: bool = False,
        **dimensions: Number,
    ):
        self._name: str
        self._dimension: Dimension = Dimension(**dimensions)
        self._is_dimensionless: bool = self._dimension._is_dimensionless
        self._is_dependent: bool = bool(dependent)
        self._is_scaling: bool = bool(scaling)
        self._symbolic: Union[Symbol, Mul, Pow, Number]
        self._is_constant: bool = False
        self._is_number: bool = False
        self._is_quotient: bool = False
        self._is_reduced: bool = True
        self._unreduced: Quantity = self
        self._base: Quantity
        self._exponent: Number
        self._factors: list[Quantity]
        self._validate_quantity()
        self._set_quantity_name(name)
        self._set_symbolic_quantity()

    @property
    def name(self) -> str:
        return self._name

    @property
    def dimension(self) -> Dimension:
        return self._dimension

    @property
    def is_dependent(self) -> bool:
        return self._is_dependent

    @property
    def is_scaling(self) -> bool:
        return self._is_scaling

    @property
    def is_dimensionless(self) -> bool:
        return self._is_dimensionless

    def _validate_quantity(self):
        if self._is_dependent and self._is_constant:
            raise ValueError("A constant can not be dependent")
        elif self._is_scaling and self._is_constant:
            raise ValueError("A constant can not be scaling")
        elif self._is_dependent and self._is_scaling:
            raise ValueError("A quantity can not be both dependent and scaling")
        elif self._is_scaling and self._is_dimensionless:
            raise ValueError("A quantity can not be both scaling and dimensionless")

    def _set_quantity_name(self, name: str):
        if not isinstance(name, str):
            raise TypeError("Quantity name must be a string")
        elif name.strip() == '':
            raise ValueError("Invalid quantity name")

        self._name = name

    def _set_symbolic_quantity(self):
        self._symbolic = Symbol(self._name)

    def _copy(self):
        qty_copy = eval(srepr(self))
        qty_copy._unreduced = self._unreduced
        return qty_copy

    def reduce(self):
        if self._is_reduced:
            return self
        elif self._is_power:
            from nodimo.power import Power

            base = self.base.reduce()
            exponent = self.exponent
            reduced_power = Power(
                base,
                exponent,
                name=self._name,
                dependent=self._is_dependent,
                scaling=self._is_scaling,
            )
            reduced_power._unreduced = self
            return reduced_power
        elif self._is_product:
            from nodimo.product import Product

            factors = [qty.reduce() for qty in self.factors]
            reduced_product = Product(
                *factors,
                name=self._name,
                dependent=self._is_dependent,
                scaling=self._is_scaling,
            )
            reduced_product._unreduced = self
            return reduced_product

    def _key(self) -> tuple:
        return (self._name, frozenset(self._dimension.items()))

    def __hash__(self) -> int:
        return hash(self._key())

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        elif isinstance(other, type(self)):
            return self._key() == other._key()
        return False

    def __mul__(self, other):
        if not isinstance(other, Quantity):
            raise NotImplementedError(f"{self} and {other} cannot be multiplied")

        from nodimo.product import Product

        return Product(self, other)

    def __pow__(self, exponent: Number):
        from nodimo.power import Power

        return Power(self, exponent)

    def __truediv__(self, other):
        if not isinstance(other, Quantity):
            raise NotImplementedError(f"{other} cannot divide {self}")

        return self * other**-1

    def __str__(self) -> str:
        return sstr(self)

    def _repr_latex_(self):
        """Latex representation according to IPython/Jupyter."""

        return f'$\\displaystyle {latex(self)}$'

    def _sympy_(self):
        return self._symbolic

    def _sympyrepr(self, printer):
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        name = f"'{self.name}'" if self.name is not None else ''
        dimensions = ''
        if not self._is_dimensionless:
            dim_exp = []
            for dim, exp in self._dimension.items():
                exp_ = _unsympify_number(exp)
                dim_exp.append(f'{dim}={repr(exp_)}')
            dimensions = f", {', '.join(dim_exp)}"
        dependent = f', dependent=True' if self._is_dependent else ''
        scaling = f', scaling=True' if self._is_scaling else ''

        return f'{class_name}({name}{dimensions}{dependent}{scaling})'

    def _sympystr(self, printer):
        """User string representation according to Sympy."""

        if self._symbolic.is_number:
            printer._settings['root_notation'] = True
        else:
            printer._settings['root_notation'] = False

        return printer._print(self._symbolic)

    _pretty = _latex = _sympystr
    __repr__ = __str__


# Alias for the class Quantity to facilitate the instantiation.
Q = Quantity


class Constant(Quantity):
    """Dimensionless constant.

    Constants are most commonly just dimensionless numbers. Here, they
    can be represented by letters, which are be provided as the value
    parameter. If the value is a string of characters, the constant is
    printed in bold on the screen to avoid confusion with instances of
    Quantity.

    Constants were implemented to allow the creation of expressions that
    contain dimensionless numbers. In general, these numbers are only
    useful in the mathematical equations that represent the model. In
    Nodimo, constants are used only for aesthetic purposes, mainly in
    product of quantities.

    Examples
    --------
    * Drag coefficient

    Dimensions: mass ``M``, length ``L`` and time ``T``.

    Quantities: drag force ``Fd``, fluid density ``rho``,
    velocity ``V``, reference area ``A``, ``half`` and
    drag coefficient ``Cd``.

    In this example, the ``reduce`` parameter set to ``False`` is
    important to keep the constant in the denominator of the expression.

    >>> from nodimo import Quantity, Power, Product
    >>> from nodimo.quantity import Constant
    >>> Fd = Quantity('F_D', M=1, L=1, T=-2)
    >>> rho = Quantity('rho', M=1, L=-3)
    >>> V = Quantity('V', L=1, T=-1)
    >>> A = Quantity('A', L=2)
    >>> half = Constant(1/2)
    >>> half_inv = Power(half, -1, reduce=False)
    >>> Cd = Product(Fd, half_inv, rho**-1, V**-2, A**-1, reduce=False)
    """

    def __new__(cls, value: Union[str, Number]):
        converted_value = cls._convert_value(value)
        if converted_value == 1:
            return One()
        return super().__new__(cls)

    def __init__(self, value: Union[str, Number]):
        self._constant_name: str
        converted_value = self._convert_value(value)
        super().__init__(str(converted_value))
        self._set_constant(converted_value)

    @classmethod
    def _convert_value(self, value: Union[str, Number]) -> Union[str, Number]:
        converted_value: Union[str, Number]
        try:
            converted_value = _sympify_number(value)
        except:
            if not isinstance(value, str):
                raise TypeError(f"Constant value must be a string or a number")
            converted_value = value

        return converted_value

    def _set_constant(self, value: Union[str, Number]):
        self._is_constant = True
        self._constant_name = str(value)
        if isinstance(value, str):
            self._name = _prettify_name(value, bold=True)
            self._set_symbolic_quantity()
        else:
            self._symbolic = value
            self._is_number = True
            if value.is_Rational and not value.is_Integer:
                self._is_quotient = True
            elif value.is_Mul:
                for num in value.args:
                    if num.is_Rational and not num.is_Integer:
                        self._is_quotient = True
                        break
                    elif num.is_Pow and Pow(num, 1).exp < 0:
                        self._is_quotient = True
                        break

    def _sympyrepr(self, printer):
        class_name = type(self).__name__
        if self._is_number and self._symbolic.is_Number:
            value = _unsympify_number(self._symbolic)
        else:
            value = f"'{self._constant_name}'"

        return f'{class_name}({value})'


class One(Constant):
    """Dimensionless one."""

    _is_one = True

    def __new__(cls, *args, **kwargs):
        return super(Constant, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(1)

    def _sympyrepr(self, printer):
        return f'{type(self).__name__}()'
