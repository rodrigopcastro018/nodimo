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
One
    Creates the dimensionless number one.
"""

from sympy import sstr, srepr, latex, Symbol, Mul, Pow, Number
from sympy.printing.pretty.stringpict import prettyForm
from typing import Optional, Union

from nodimo.dimension import Dimension
from nodimo._internal import _unsympify_number


class Quantity:
    """Base class for quantities.

    Most basic type of physical quantity, with attributes that are
    useful in describing its dimensional properties.

    Parameters
    ----------
    name : str
        Name to be used as the quantity representation.
    dependent : bool, default=False
        If ``True``, the quantity is dependent.
    scaling : bool, default=False
        If ``True``, the quantity can be used as scaling parameter.
    **dimensions : Number
        The dimensions of the quantity given as keyword arguments.

    Attributes
    ----------
    name : str
        Name used as the quantity representation.
    dimension : Dimension
        The quantity dimension.
    is_dependent : bool
        If ``True``, the quantity is dependent.
    is_scaling : bool
        If ``True``, the quantity can be used as scaling parameter.
    is_dimensionless : bool
        If ``True``, the quantity is dimensionless.

    Raises
    ------
    TypeError
        If the quantity name is not an non-empty string.
    ValueError
        If the quantity name is invalid.
    ValueError
        If the quantity is set as both dependent and scaling.
    ValueError
        If the quantity is set as scaling, but with no dimensions.
    """

    _is_quantity: bool = True
    _is_power: bool = False
    _is_product: bool = False
    _is_constant: bool = False
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
        self._symbolic: Union[Symbol, Mul, Pow]
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

    @is_dependent.setter
    def is_dependent(self, dependent: bool):
        self._validate_quantity(is_dependent=dependent)
        self._is_dependent = bool(dependent)

    @property
    def is_scaling(self) -> bool:
        return self._is_scaling

    @is_scaling.setter
    def is_scaling(self, scaling: bool):
        self._validate_quantity(is_scaling=scaling)
        self._is_scaling = bool(scaling)

    @property
    def is_dimensionless(self) -> bool:
        return self._is_dimensionless

    def _validate_quantity(
        self,
        is_dependent: Optional[bool] = None,
        is_scaling: Optional[bool] = None,
    ):
        if is_dependent is None:
            is_dependent = self._is_dependent
        if is_scaling is None:
            is_scaling = self._is_scaling

        if is_dependent and is_scaling:
            raise ValueError("A quantity can not be both dependent and scaling")
        elif is_scaling and self._is_dimensionless:
            raise ValueError("A quantity can not be both scaling and dimensionless")

    def _set_quantity_name(self, name: str):
        if not isinstance(name, str):
            raise TypeError("Quantity name must be a non-empty string")
        elif name.strip() == '':
            raise ValueError("Invalid quantity name")

        self._name = name

    def _set_symbolic_quantity(self):
        # To preserve Product factors order, commutative=False.
        self._symbolic = Symbol(self._name, commutative=False)

    def _copy(self):
        return eval(srepr(self))

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
            raise NotImplemented
        
        from .product import Product
        
        return Product(self, other)

    def __pow__(self, exponent: Number):
        from .power import Power

        return Power(self, exponent)

    def __truediv__(self, other):
        if not isinstance(other, Quantity):
            raise NotImplemented

        return self * other**-1

    def __str__(self) -> str:
        return sstr(self)

    def _repr_latex_(self):
        """Latex representation according to IPython/Jupyter."""

        return f'$\\displaystyle {latex(self)}$'

    def _sympy_(self):
        return self._symbolic

    def _sympyrepr(self, printer) -> str:
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

    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy."""
        
        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.

        return printer._print(self._symbolic)

    _latex = _pretty = _sympystr
    __repr__ = __str__


# Alias for the class Quantity to facilitate the creation of instances.
Q = Quantity


# class One(Quantity):  # TODO: delete this later
#     """Dimensionless one."""

#     _is_one = True
    
#     def __init__(self):
#         super().__init__('One')
#         self._name = ''
#         self._symbolic = S.One

#     @property
#     def is_dependent(self) -> bool:
#         return self._is_dependent
    
#     @property
#     def is_scaling(self) -> bool:
#         return self._is_scaling


# class Constant(Quantity):
#     """Dimensionless constant.

#     Constants are most commonly just dimensionless numbers. Here, they
#     are preferably represented by letters, which can be provided as the
#     name parameter. Constants are printed differently on the screen to
#     avoid confusion with instances of Quantity. In latex, a calligraphic
#     style is adopted, while the Cnst() operator is employed to identify
#     contants in non-latex displays.
#     """

#     _is_constant = True

#     def __init__(self, name: str = 'C'):
#         super().__init__(name)
#         self._name = f'Constant({name})'

#     @property
#     def is_dependent(self) -> bool:
#         return self._is_dependent
    
#     @property
#     def is_scaling(self) -> bool:
#         return self._is_scaling

#     def _sympystr(self, printer) -> str:
#         printer.set_global_settings(root_notation=False)

#         return f'Cnst({printer._print(self._symbolic)})'

#     def _latex(self, printer) -> str:
#         printer.set_global_settings(root_notation=False)

#         return f'\\mathcal{{{printer._print(self._symbolic)}}}'

#     def _pretty(self, printer) -> prettyForm:
#         printer.set_global_settings(root_notation=False)

#         cnst = prettyForm('Cnst')
#         constant = prettyForm(*printer._print(self._symbolic).parens())

#         return prettyForm(*cnst.right(constant))


class Constant(Quantity):
    """Dimensionless constant.

    Constants are most commonly just dimensionless numbers. Here, they
    are preferably represented by letters, which can be provided as the
    name parameter. Constants are printed differently on the screen to
    avoid confusion with instances of Quantity. In latex, a calligraphic
    style is adopted, while the Cnst() operator is employed to identify
    contants in non-latex displays.
    """

    _is_constant = True

    def __init__(self, name: str = 'C'):
        super().__init__(name)
        self._name = f'Const({name})'

    @property
    def is_dependent(self) -> bool:
        return self._is_dependent
    
    @property
    def is_scaling(self) -> bool:
        return self._is_scaling

    def _sympystr(self, printer) -> str:
        printer.set_global_settings(root_notation=False)

        return self._name

    def _latex(self, printer) -> str:
        printer.set_global_settings(root_notation=False)

        return f'\\mathcal{{{printer._print(self._symbolic)}}}'

    def _pretty(self, printer) -> prettyForm:
        printer.set_global_settings(root_notation=False)

        cnst = prettyForm('Const')
        constant = prettyForm(*printer._print(self._symbolic).parens())

        return prettyForm(*cnst.right(constant))


class One(Constant):
    """Dimensionless one."""

    _is_one = True
    
    def __init__(self):
        super().__init__('1')

    def _sympystr(self, printer) -> str:
        printer.set_global_settings(root_notation=False)

        return printer._print(self._symbolic)

    _latex = _pretty = _sympystr