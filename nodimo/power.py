"""
=================================
Power (:mod:`nodimo.power`)
=================================

This module contains the classes to create a variable power.

Classes
-------
BasicPower
    Base class for the power of a variable.
Power
    Creates a symbolic power of a variable.
"""

from sympy import Symbol, Pow, Rational

from nodimo.variable import Variable, OneVar
from nodimo._internal import _sympify_number, _repr


class Power(Variable):
    """Base class for the power of a variable.

    Base class that represents the power of a variable. The dimensional
    properties of the power are calculated from the input variable and
    the exponent.

    Parameters
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Rational
        Exponent to which the variable will be raised.
    name : Optional[str], default=None
        Name to be used in string representation.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
    name : Optional[str]
        Name to be used in string representation.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the power is dependent.
    is_scaling : bool
        If ``True``, the power can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the power is nondimensional.

    Raises
    ------
    ValueError
        If the power is set as both dependent and scaling.
    ValueError
        If the power is set as scaling when it has no dimensions.
    """

    def __new__(
        cls,
        variable: Variable,
        exponent: Rational,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):
        
        exponent_sp = _sympify_number(exponent)

        if isinstance(variable, Power):
            exponent_sp *= variable._exponent
            variable = variable._variable
        
        if exponent_sp == 0:
            return OneVar()
        elif exponent_sp == 1:
            return variable
        else:
            return super().__new__(cls)

    def __init__(
        self,
        variable: Variable,
        exponent: Rational,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):

        exponent_sp = _sympify_number(exponent)
        
        if isinstance(variable, Power):
            exponent_sp *= variable._exponent
            variable = variable._variable

        self._variable: Variable = variable
        self._exponent: Rational = exponent_sp
        
        super().__init__(name=name)
        self._set_dimensions()
        self.is_dependent = dependent
        self.is_scaling = scaling
        self._depth += variable._depth

    @property
    def variable(self) -> Variable:
        return self._variable

    @property
    def exponent(self) -> Rational:
        return self._exponent
    
    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    # def combine(self, name: Optional[str] = None) -> BasicCombinedVariable:
    #     """Converts to a combined variable."""

    #     return BasicCombinedVariable(self, name)

    def _build_symbolic(self):
        """Builds symbolic representation in Sympy."""

        if self.name:
            self._symbolic = Symbol(self.name)
        else:
            self._symbolic = Pow(self._variable.symbolic, self._exponent)

    def _set_dimensions(self):
        """Evaluates the dimensions of the power."""

        if self._variable.is_nondimensional:
            pass
        else:
            dimensions = {}
            for dim, exp in self._variable.dimensions.items():
                dimensions[dim] = exp * self._exponent
            
            self._dimensions = dimensions
            self._is_nondimensional = all(dim == 0 for dim in dimensions.values())

    def _to_product(self):
        """Converts the power of a product to the product of powers."""

        from nodimo.product import Product

        if isinstance(self._variable, Product):
            powers = []
            for var in self._variable.variables:
                powers.append(Power(var, self._exponent))
            return Product(*powers)
        else:
            return self

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variable_repr = _repr(self._variable)
        exponent_repr = f', {_repr(self._exponent)}'
        name_repr = f", name='{self.name}'" if self.name else ''
        dependent_repr = f', dependent=True' if self.is_dependent else ''
        scaling_repr = f', scaling=True' if self.is_scaling else ''

        return (f'{class_name}('
                + variable_repr
                + exponent_repr
                + name_repr
                + dependent_repr
                + scaling_repr
                + ')')
