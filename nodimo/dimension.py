#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Product
=======

This module contains the class to create a quantity dimension.

Classes
-------
Dimension
    Creates the dimension of a quantity.
"""

from sympy import sstr, srepr, latex, Symbol, Mul, Number, S
from sympy.printing.pretty.stringpict import prettyForm
from typing import Union

from nodimo._internal import _sympify_number, _unsympify_number


class Dimension(dict):
    """The dimension of a quantity.

    This class inherits from dictionary and adds to it representation
    methods to display the dimension of a quantity in the way that is
    conventionally done by the literature and by the ISO 80000-1.

    Parameters
    ----------
    **dimensions : Number
        Base dimensions and exponents given as keyword arguments.
    """

    def __init__(self, **dimensions: Number):
        self._dimensions: dict[str, Number]
        self._is_dimensionless: bool
        self._symbolic: Mul
        self._set_dimensions(**dimensions)
        super().__init__(**self._dimensions)
        self._set_symbolic_dimension()

    def _set_dimensions(self, **dimensions: Number):
        """Sympifies and clear null dimensional exponents."""

        dimensions_sp = {}
        for dim, exp in dimensions.items():
            exp_sp = _sympify_number(exp)
            if exp_sp != 0:
                dimensions_sp[dim] = exp_sp

        self._dimensions = dimensions_sp
        self._is_dimensionless = all(dim == 0 for dim in dimensions_sp.values())

    def _set_symbolic_dimension(self):
        if self._is_dimensionless:
            self._symbolic = S.One
        else:
            factors = []
            for dim, exp in self.items():
                dim_symbol = Symbol(dim, commutative=False)
                factors.append(dim_symbol**exp)
            self._symbolic = Mul(*factors, evaluate=False)

    def _copy(self):
        return eval(srepr(self))

    def __mul__(self, other):
        if not isinstance(other, Dimension):
            raise NotImplementedError(f"{self} and {other} cannot be multiplied")

        dimensions = self._dimensions.copy()
        for dim, exp in other.items():
            if dim in dimensions:
                dimensions[dim] += exp
            else:
                dimensions[dim] = exp

        return Dimension(**dimensions)

    def __pow__(self, exponent: Number):
        exponent_sp = _sympify_number(exponent)
        dimensions = {}
        for dim, exp in self.items():
            dimensions[dim] = exp * exponent_sp

        return Dimension(**dimensions)

    def __truediv__(self, other):
        if not isinstance(other, Dimension):
            raise NotImplementedError(f"{other} cannot divide {self}")

        return self * other**-1

    def __str__(self) -> str:
        return sstr(self)

    __repr__ = __str__

    def _repr_latex_(self):
        """Latex representation according to IPython/Jupyter."""

        return f'$\\displaystyle {latex(self)}$'

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        dimensions = ''
        if not self._is_dimensionless:
            dim_exp = []
            for dim, exp in self.items():
                exp_ = _unsympify_number(exp)
                dim_exp.append(f'{dim}={repr(exp_)}')
            dimensions = ', '.join(dim_exp)

        return f'{class_name}({dimensions})'

    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy."""

        if self._is_dimensionless:
            return printer._print(self._symbolic)

        printer._settings['root_notation'] = True
        exponents = []
        for expt in self._dimensions.values():
            if expt < 0 or expt.is_Mul:
                exponent = f'({printer._print(expt)})'
            elif expt.is_Rational and not expt.is_Integer:
                exponent = f'({printer._print(expt)})'
            else:
                exponent = printer._print(expt)
            exponents.append(exponent)

        printer._settings['root_notation'] = False
        dimensions = []
        for dim, exp in zip(self._dimensions, exponents):
            if self._dimensions[dim] != 1:
                dimensions.append(f'{printer._print(dim)}**{exp}')
            else:
                dimensions.append(printer._print(dim))

        return '*'.join(dimensions)

    def _latex(self, printer) -> str:
        """User string representation according to Sympy.

        The dimension's symbol use the Sans Serif font to follow the
        conventional dimension representation.
        """

        if self._is_dimensionless:
            return f'\\mathsf{{{printer._print(self._symbolic)}}}'

        printer._settings['root_notation'] = True
        exponents = []
        for exp in self._dimensions.values():
            exponents.append(printer._print(exp))

        printer._settings['root_notation'] = False
        dimensions = []
        for dim, exp in zip(self._dimensions, exponents):
            if self._dimensions[dim] != 1:
                dimensions.append(f'\\mathsf{{{dim}}}^{{{exp}}}')
            else:
                dimensions.append(f'\\mathsf{{{dim}}}')

        return ' '.join(dimensions)

    def _pretty(self, printer) -> prettyForm:
        """Pretty representation according to Sympy."""

        if self._is_dimensionless:
            return printer._print(self._symbolic)

        printer._settings['root_notation'] = True
        exponents = []
        for exp in self._dimensions.values():
            exponents.append(printer._print(exp))

        printer._settings['root_notation'] = False
        for i, (dim, exp) in enumerate(zip(self._dimensions, exponents)):
            dimexp = printer._print(dim)
            if self._dimensions[dim] != 1:
                dimexp = dimexp**exp
            if i == 0:
                dimension = dimexp
            else:
                dimension *= dimexp

        return dimension
