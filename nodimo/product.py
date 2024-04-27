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

from sympy import Symbol, Mul, S
from typing import Optional

from nodimo.variable import Variable, Variable, OneVar
from nodimo.matrix import BasicDimensionalMatrix
from nodimo.power import Power, Power
from nodimo._internal import _repr


class Product(Variable):
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
    
    _depth: int = 1

    def __new__(
        cls,
        *variables: Variable,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):

        if len(variables) == 0:
            return OneVar()
        if len(variables) == 1:
            var = variables[0]
            if isinstance(var, Product):
                return super().__new__(cls)
            return var
        else:
            return super().__new__(cls)

    def __init__(
        self,
        *variables: Variable,
        name: str = '',
        dependent: bool = False,
        scaling: bool = False,
    ):

        self._variables: tuple[Variable] = variables
        self._base_variables: tuple[Variable]
        super().__init__(name=name)
        self._simplify()

        var1 = self._variables[0]
        var2 = Product(*self._variables[1:])
        self._set_dimensions(var1, var2)  # TODO: Check if i really need this class to work as a binary operator. Couldn't i evaluate the dimensions all at once?

        self.is_dependent = dependent
        self.is_scaling = scaling
        self._depth += max(var._depth for var in variables)

    @property
    def variables(self) -> tuple[Variable]:
        return self._variables

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
            var_symb = []
            for var in self._variables:
                var_symb.append(var.symbolic)
            self._symbolic = Mul(*var_symb)

    def _set_dimensions(self, var1, var2):
        """Evaluates the dimensions of the product of two variables."""

        if var1.is_nondimensional and var2.is_nondimensional:
            pass
        elif var1.is_nondimensional:
            self._dimensions = var2.dimensions
        elif var2.is_nondimensional:
            self._dimensions = var1.dimensions
        else:
            dimensional_matrix = BasicDimensionalMatrix(var1, var2)
            exponents = []
            for row in dimensional_matrix._raw_matrix:
                exponents.append(sum(row))
            
            self._dimensions = dict(zip(dimensional_matrix.dimensions, exponents))
            self._clear_null_dimensions()

        self._is_nondimensional = all(dim == 0 for dim in self._dimensions.values())

    def _simplify(self):
        """Simplifies the multiplication factors."""

        self._clear_ones()  # To not use OneVar() as base variable.
        self._products_to_factors()
        self._set_base_variables()
        if len(self._variables) > len(self._base_variables):
            self._factors_to_powers()
        self._clear_ones()  # Removes canceled base variables.

    def _clear_ones(self):
        """Removes instances of OneVar."""

        variables = []
        for var in self._variables:
            if not isinstance(var, OneVar):
                variables.append(var)

        self._variables = tuple(variables)
    
    def _products_to_factors(self):
        """Susbtitutes products by its factors."""

        variables = list(self._variables)
        depth = max(var._depth for var in variables)

        for _ in range(depth):
            new_variables = []
            for var in variables:
                if isinstance(var, Product):
                    new_variables.extend(var._variables)
                elif isinstance(var, Power):
                    new_var = var._to_product()
                    if new_var is var:
                        new_variables.append(var)
                    else:
                        new_variables.extend(new_var._variables)
                else:
                    new_variables.append(var)
            variables = new_variables.copy()

        self._variables = tuple(variables)

    def _set_base_variables(self):
        """Determines the base variables.

        Base variables are instances of Variable and
        CombinedVariable.
        """

        base_variables = []
        for var in self._variables:
            if isinstance(var, Power):
                base_var = var._variable
            else:
                base_var = var

            if base_var not in base_variables:
                base_variables.append(base_var)
        
        self._base_variables = tuple(base_variables)
    
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

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = _repr(self._variables)[1:-1]
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
