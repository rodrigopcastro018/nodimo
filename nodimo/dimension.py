from sympy import sstr, latex, Symbol, Mul, Number, S
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
        self._symbolic: Union[S.One, Mul]
        self._set_dimension(**dimensions)
        super().__init__(**self._dimensions)
        self._set_symbolic_dimension()

    def _set_dimension(self, **dimensions: Number):
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
            self._symbolic = Mul(*factors)

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

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.

        def _print(expr):
            if expr.is_Pow:
                # Rational=True is set to avoid the 'sqrt'
                # operator on the string representation.
                return printer._print_Pow(expr, rational=True)
            else:
                return printer._print(expr)

        if self._symbolic.is_Mul:
            return '*'.join(_print(f) for f in self._symbolic.args)
        
        return _print(self._symbolic)

    def _pretty(self, printer):
        """Pretty representation according to Sympy."""

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.
        
        return printer._print(self._symbolic)

    def _latex(self, printer) -> str:
        """User string representation according to Sympy.
        
        The latex expression is built using a Sans Serif font to follow
        the conventional dimension representation.
        """

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.

        return f'\\mathsf{{{printer._print(self._symbolic)}}}'

    __repr__ = __str__
