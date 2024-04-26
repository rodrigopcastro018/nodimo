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

from sympy import Mul, S
from typing import Optional

from nodimo.variable import Variable, Variable, OneVar
from nodimo.matrix import BasicDimensionalMatrix
from nodimo.power import BasicPower, Power
from nodimo._internal import _repr


class Multiplication:
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

    Methods
    -------
    simplify()
        Simplifies the multiplication factors.
    """

    def __init__(self, *variables: Variable):

        self._variables: tuple[Variable] = variables
        self._base_variables: tuple[Variable]

    @property
    def variables(self) -> tuple[Variable]:
        return self._variables
    
    def simplify(self):
        """Simplifies the multiplication factors.

        The simplification is described by the following example:
        
        a * (a * b**2) * 1 -> a * (a * b**2)
        a * (a * b**2)     -> a * a * b**2
        a * a * b**2       -> a**2 * b**2
        """

        self._clear_ones()
        self._products_to_factors()
        self._set_base_variables()
        if len(self._variables) > len(self._base_variables):
            self._factors_to_powers()

    def _clear_ones(self):
        """Removes instances of OneVar."""

        variables = []
        
        for var in self._variables:
            if not isinstance(var, OneVar):
                variables.append(var)

        self._variables = tuple(variables)
    
    def _products_to_factors(self):
        """Susbtitutes products by its factors."""

        new_variables = list(self._variables)
        is_mul = [isinstance(var, Multiplication) for var in new_variables]

        while any(is_mul):
            variables = []
            for var in new_variables:
                if isinstance(var, Multiplication):
                    variables.extend(var._variables)
                else:
                    variables.append(var)
            new_variables = variables.copy()
            is_mul = [isinstance(var, Multiplication) for var in new_variables]

        self._variables = tuple(new_variables)

    def _set_base_variables(self):
        """Determines the base variables.

        Base variables are instances of BasicVariable and
        BasicCombinedVariable.
        """

        base_variables = []
        for var in self._variables:
            if isinstance(var, BasicPower):
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
                elif isinstance(var, BasicPower):
                    if var._variable == base_var:  # TODO: turn BasicPower._variable and ._exponent into a property.
                        exponent += var._exponent

            if isinstance(base_var, (Variable, CombinedVariable)):
                variables.append(Power(base_var, exponent))
            elif isinstance(base_var, (Variable, BasicCombinedVariable)):
                variables.append(BasicPower(base_var, exponent))

        self._variables = tuple(variables)


class BasicProduct(Variable, Multiplication):
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
    
    def __new__(
        cls,
        *variables: Variable,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False,
    ):

        if len(variables) == 0:
            return OneVar()
        if len(variables) == 1:
            var = variables[0]
            if isinstance(var, BasicProduct):
                return super().__new__(cls)
            return var
        else:
            return super().__new__(cls)

    def __init__(
        self,
        *variables: Variable,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False,
    ):

        super().__init__(name=name)
        Multiplication.__init__(self, *variables)

        var1 = variables[0]
        var2 = BasicProduct(*variables[1:])
        self._set_dimensions(var1, var2)  # TODO: Check if i really need this class to work as a binary operator. Couldn't i evaluate the dimensions all at once?

        self.is_dependent = dependent
        self.is_scaling = scaling

    # Redefining dimensions as a read-only property
    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    # def combine(self, name: Optional[str] = None) -> BasicCombinedVariable:
    #     """Converts to a combined variable."""

    #     return BasicCombinedVariable(self, name)

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

    def __str__(self) -> str:
        
        if self.name is not None:
            return self.name
        else:
            return ' * '.join(str(var) for var in self._variables)

    def __repr__(self) -> str:

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


class Product(Mul, BasicProduct):
    """Creates a symbolic product of variables.

    This class inherits the dimensional properties of BasicProduct and
    adds to it, by inheriting from sympy.Mul, the ability to be used
    in symbolic mathematical expressions.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that compose the product.
    name : Optional[str], default=None
        The name that will be displayed in symbolic expressions.
    dependent : bool, default=False
        If ``True``, the product is dependent.
    scaling : bool, default=False
        If ``True``, the product can be used as scaling parameter.

    Attributes
    ----------
    name : Optional[str]
        The name that will be displayed in symbolic expressions.
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

    def __new__(  # FIXME: There is a problem when the *variables are all the same or a 'Power' of each other. The return type is of type sympy.Pow
        cls,
        *variables: Variable,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False,
    ):

        if len(variables) <= 1:
            return super().__new__(cls, *variables)
        else:
            return Mul.__new__(cls, *variables)

    def __init__(
        self,
        *variables: Variable,
        name: Optional[str] = None,
        dependent: bool = False,
        scaling: bool = False,
    ):

        super().__init__(*variables, name=name, dependent=dependent, scaling=scaling)

    # def combine(self, name: Optional[str] = None) -> CombinedVariable:
    #     """Converts to a combined variable."""

    #     return CombinedVariable(self, name)

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        if self.name:
            return printer._print_Symbol(self)
        else:
            return printer._print_Mul(self)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        return BasicProduct.__repr__(self)

    _latex = _pretty = _sympystr


Prod = Product
