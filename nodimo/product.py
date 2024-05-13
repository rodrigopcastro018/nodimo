"""
=================================
Variable (:mod:`nodimo.variable`)
=================================

This module contains the classes to create a product of variables.

Classes
-------
BasicProduct
    Base class for the product of variables.
Product
    Creates a symbolic product of variables.
"""

from sympy import Symbol, Mul, S, Rational, sstr, srepr

from nodimo.variable import Variable, Variable, OneVar
from nodimo.groups import Collection
from nodimo.power import Power


class BasicProduct(Collection):
    """Multiplication operator.

    To not be confused with the class Product, which represents the
    multiplication result. This class provides the possibility of
    simplifying the multiplication operator.

    Parameters
    ----------
    *variables : BasicVariable
        Variables to be multiplied.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        Variables to be multiplied.
    """
    
    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._set_base_variables()
        self._set_product_dimensions()
        
        self._original_variables: tuple[Variable] = tuple(list(self._variables))
        self._variables: tuple[Variable] = tuple(list(self._disassembled_variables))

        self._is_simplifiable: bool = (
            len(self._disassembled_variables) != len(self._base_variables)
        )

        if self._is_simplifiable:
            self._simplify()

    @property
    def variables(self) -> tuple[Variable]:
        return self._variables

    def _set_product_dimensions(self):
        """Evaluates the dimensions of the product."""

        dimensions = {}
        for dim in self._dimensions:
            exp = S.Zero
            for var in self._variables:
                if dim in var.dimensions.keys():
                    exp += var.dimensions[dim]
            dimensions[dim] = exp

        self._dimensions = dimensions

    def _simplify(self):
        """Simplifies the multiplication factors."""

        self._factors_to_powers()
        self._variables = self._clear_ones(*self._variables)
    
    def _factors_to_powers(self):
        """Converts factors with same base variable to power."""

        variables = []
        for base_var in self._base_variables:
            exponent = S.Zero
            for var in self._variables:
                if var == base_var:
                    exponent += S.One
                elif isinstance(var, Power):
                    if var._variable == base_var:
                        exponent += var._exponent

            variables.append(Power(base_var, exponent))

        self._variables = tuple(variables)

    def __str__(self) -> str:
        
        return ' * '.join(sstr(var) for var in self._variables)


class Product(Variable, BasicProduct):
    """Base class for the product of variables.

    Base class that represents the product of variables. The dimensional
    properties of the product are calculated from the input variables.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that compose the product.
    name : Optional[str], default=None
        Name to be used in string representation.
    dependent : bool, default=False
        If ``True``, the product is dependent.
    scaling : bool, default=False
        If ``True``, the product can be used as scaling parameter.
    simplify : bool, default=False
        If ``True``, the multiplication factors get simplified.

    Attributes
    ----------
    name : Optional[str]
        Name to be used in string representation.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the product is dependent.
    is_scaling : bool
        If ``True``, the product can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the product is nondimensional.

    Raises
    ------
    ValueError
        If the product is set as both dependent and scaling.
    ValueError
        If the product is set as scaling when it has no dimensions.
    """

    _is_product = True

    def __new__(
        cls,
        *variables: Variable,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):

        bprod = BasicProduct(*variables)
        if bprod._is_simplifiable:
            variables = bprod._variables

        if len(variables) == 0:
            return OneVar()
        if len(variables) == 1:
            return variables[0]
        else:
            return super().__new__(cls)

    def __init__(
        self,
        *variables: Variable,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):

        BasicProduct.__init__(self, *variables)
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
            var_symb = []
            for var in self._variables:
                var_symb.append(var.symbolic)
            self._symbolic = Mul(*var_symb)

    def _key(self) -> tuple:

        return (frozenset(self._variables),)

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join(srepr(var) for var in self._variables)
        name_repr = f", name='{self.name}'" if self.name else ''
        dependent_repr = f', dependent=True' if self.is_dependent else ''
        scaling_repr = f', scaling=True' if self.is_scaling else ''

        return (f'{class_name}('
                + variables_repr
                + name_repr
                + dependent_repr
                + scaling_repr
                + ')')


Prod = Product
