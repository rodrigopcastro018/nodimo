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

from sympy import Symbol, Pow, Rational, S, srepr, sstr

from nodimo.variable import Variable, OneVar
from nodimo._internal import _sympify_number, _unsympify_number


class BasicPower:
    """Exponentiation operator.

    To not be confused with the class Power, which represents the
    exponentiation result. This class operates some simplifications
    on the exponentiation operator.

    Parameters
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Rational
        Exponent to which the variable will be raised.

    Attributes
    ----------
    variable : BasicVariable
        Variable to be exponentiated.
    exponent : Rational
        Exponent to which the variable will be raised.
    """

    def __init__(self, variable: Variable, exponent: Rational):

        exponent_sp = _sympify_number(exponent)
        
        if isinstance(variable, Power):
            exponent_sp *= variable._exponent
            variable = variable._variable

        self._variable: Variable = variable
        self._exponent: Rational = exponent_sp
        self._dimensions: dict[str, Rational]
        self._set_power_dimensions()
    
    @property
    def variable(self) -> Variable:
        return self._variable

    @property
    def exponent(self) -> Rational:
        return self._exponent
    
    def _set_power_dimensions(self):
        """Evaluates the dimensions of the power."""

        dimensions = {}
        if not self._variable.is_nondimensional:
            for dim, exp in self._variable.dimensions.items():
                dimensions[dim] = exp * self._exponent
            
        self._dimensions = dimensions

    def __str__(self) -> str:

        variable_str = sstr(self._variable)
        exponent_str = sstr(self._exponent)
        if self._exponent < 0 or isinstance(self._exponent, Rational):
            exponent_str = f'({exponent_str})'
        
        return f'{variable_str}**{exponent_str}'

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variable_repr = srepr(self._variable)
        unsymp_exp = _unsympify_number(self._exponent)
        exp_ = f"'{unsymp_exp}'" if isinstance(unsymp_exp, str) else unsymp_exp
        exponent_repr = f', {exp_}'

        return f'{class_name}({variable_repr}{exponent_repr})'


class Power(Variable, BasicPower):
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
    name : str, default=''
        Name to be used in string representation.
    dependent : bool, default=False
        If ``True``, the power is dependent.
    scaling : bool, default=False
        If ``True``, the power can be used as scaling parameter.

    Attributes
    ----------
    name : str
        Name to be used in string representation.
    dimensions : dict[str, Rational]
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

    _is_power = True

    def __new__(
        cls,
        variable: Variable,
        exponent: Rational,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):

        if isinstance(variable, OneVar):
            return OneVar()

        bpower = BasicPower(variable, exponent)
        variable = bpower.variable
        exponent = bpower.exponent
        
        if exponent is S.Zero:
            return OneVar()
        elif exponent is S.One:
            return variable

        from .product import Product

        if isinstance(variable, Product):
            return Product(*(Power(var, exponent) for var in variable.variables))
        
        return super().__new__(cls)

    def __init__(
        self,
        variable: Variable,
        exponent: Rational,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):

        BasicPower.__init__(self, variable, exponent)
        super().__init__(name=name, **self._dimensions)
        self.is_dependent = dependent
        self.is_scaling = scaling
    
    @property
    def dimensions(self) -> dict[str, Rational]:
        return self._dimensions

    def _build_symbolic(self):
        """Builds symbolic representation in Sympy."""

        if self.name:
            self._symbolic = Symbol(self.name, commutative=False)
        else:
            var = self._variable
            # Setting com=True avoids variables with negative exponents
            # on the numerator. However, the denominator does not follow
            # input order.
            com = True if self._exponent < S.Zero else False
            self._variable._symbolic = Symbol(var.name, commutative=com)
            self._symbolic = Pow(self._variable.symbolic, self._exponent)

    def _key(self) -> tuple:
        return (self._variable, self._exponent)

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variable_repr = srepr(self._variable)

        unsymp_exp = _unsympify_number(self._exponent)
        exp_ = f"'{unsymp_exp}'" if isinstance(unsymp_exp, str) else unsymp_exp
        exponent_repr = f', {exp_}'
        
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
