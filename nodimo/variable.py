"""
=================================
Variable (:mod:`nodimo.variable`)
=================================

This module contains the class to create a symbolic variable.

Classes
-------
BasicVariable
    Base class for variables.
Variable
    Creates a symbolic variable.
"""

from sympy import Symbol, Mul, Pow, S, Rational
from sympy.core._print_helpers import Printable
from typing import Optional, Union

from nodimo._internal import _sympify_number, _unsympify_number


class Variable(Printable):
    """Base class for variables.

    Most basic type of variable, with a few attributes that are useful
    in describing its dimensional properties.

    Parameters
    ----------
    name : str, default=None
        The name that will be displayed in symbolic expressions.
    dependent : bool, default=False
        If ``True``, the variable is dependent.
    scaling : bool, default=False
        If ``True``, the variable can be used as scaling parameter.
    **dimensions : int
        The dimensions of the variable given as keyword arguments.

    Attributes
    ----------
    name : str
        The name that will be displayed in symbolic expressions.
    symbolic : Symbol
        Sympy object that represents the variable.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the variable is dependent.
    is_scaling : bool
        If ``True``, the variable can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the variable is nondimensional.

    Raises
    ------
    ValueError
        If the variable is set as both dependent and scaling.
    ValueError
        If the variable is set as scaling, but with no dimensions.
    """

    def __init__(
        self,
        name: str,  # TODO: Turn name attribute mandatory. Keep it optional on Product and Power.
        dependent: bool = False,
        scaling: bool = False,
        **dimensions: int,
    ):

        self._name: Optional[str] = name
        self._dimensions: dict[str, int] = dimensions  # TODO: Check if dict can be substituted by sympy.Dict
        self._is_dependent: bool = bool(dependent)
        self._is_scaling: bool = bool(scaling)
        self._is_nondimensional: bool = all(dim == 0 for dim in dimensions.values())
        self._symbolic: Union[Symbol, Mul, Pow]

        self._validate_properties()
        self._sympify_exponents()
        self._clear_null_dimensions()
        self._build_symbolic()

    @property                   # TODO: Make all properties immutable?
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, name: str):
        self._name = name
        self._build_symbolic()

    @property
    def symbolic(self) -> Symbol:
        return self._symbolic

    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dimensions: dict[str, int]):
        self._validate_properties(dimensions=dimensions)
        self._dimensions = dimensions
        self._sympify_exponents()
        self._clear_null_dimensions()
        self._is_nondimensional = all(dim == 0 for dim in self._dimensions.values())

    @property
    def is_dependent(self) -> bool:
        return self._is_dependent

    @is_dependent.setter
    def is_dependent(self, dependent: bool):
        self._validate_properties(is_dependent=dependent)
        self._is_dependent = bool(dependent)

    @property
    def is_scaling(self) -> bool:
        return self._is_scaling

    @is_scaling.setter
    def is_scaling(self, scaling: bool):
        self._validate_properties(is_scaling=scaling)
        self._is_scaling = bool(scaling)

    @property
    def is_nondimensional(self) -> bool:
        return self._is_nondimensional

    def _build_symbolic(self):
        """Builds symbolic representation in Sympy."""

        self._symbolic = Symbol(self.name, commutative=False)

    def _clear_null_dimensions(self):
        """Removes dimensions with exponent zero."""

        for dim, exp in self._dimensions.copy().items():
            if exp == 0:
                del self._dimensions[dim]

    def _sympify_exponents(self):
        """Converts the dimensions' exponents to Sympy numbers."""

        for dim, exp in self._dimensions.items():
            self._dimensions[dim] = _sympify_number(exp)

    def _validate_properties(
        self,
        is_dependent: Optional[bool] = None,
        is_scaling: Optional[bool] = None,
        dimensions: Optional[dict[str, int]] = None,
    ):
        """Validates variable's properties."""

        if is_dependent is None:
            is_dependent = self._is_dependent
        if is_scaling is None:
            is_scaling = self._is_scaling
        if dimensions is None:
            dimensions = self._dimensions
            is_nondimensional = self._is_nondimensional
        else:
            is_nondimensional = all(dim == 0 for dim in dimensions.values())

        if is_dependent and is_scaling:
            raise ValueError("A variable can not be both dependent and scaling")
        elif is_scaling and is_nondimensional:
            raise ValueError("A variable can not be both scaling and nondimensional")

    def __key(self) -> tuple:

        return (
            self._name,
            self._is_dependent,
            self._is_scaling,
            self._is_nondimensional,
            frozenset(self._dimensions.items()),
        )

    def __hash__(self) -> int:

        return hash(self.__key())

    def __eq__(self, other) -> bool:  # TODO: Implement this method for all childs of this class

        if self is other:
            return True
        elif isinstance(other, type(self)):
            return self.__key() == other.__key()
        return False

    def __mul__(self, other):

        if not isinstance(other, Variable):
            raise NotImplemented
        
        from .product import Product
        
        return Product(self, other)

    def __pow__(self, exponent: Rational):

        from .power import Power

        return Power(self, exponent)

    def __truediv__(self, other):

        if not isinstance(other, Variable):
            raise NotImplemented

        return self * other**-1

    # TODO: define __str__ and __repr__ how they are traditionally done, because Printable defines: __str__ = __repr__ = sstr

    def _sympy_(self):
        """Sympified variable."""

        return self._symbolic

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""
        
        class_name = type(self).__name__
        name_repr = f"'{self.name}'" if self.name is not None else ''

        if self._is_nondimensional:
            dimensions_repr = ''
        else:
            dimensions = []
            for dim_name, dim_exp in self.dimensions.items():
                dim_exp_ = _unsympify_number(dim_exp)
                if isinstance(dim_exp_, str):
                    dim_exp_ = f"'{dim_exp_}'"
                dimensions.append(f'{dim_name}={dim_exp_}')
            dimensions_repr = f", {', '.join(dimensions)}"
        
        dependent_repr = f', dependent=True' if self._is_dependent else ''
        scaling_repr = f', scaling=True' if self._is_scaling else ''

        return (f'{class_name}('
                + name_repr
                + dimensions_repr
                + dependent_repr
                + scaling_repr
                + ')')

    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy."""
        
        return printer._print(self._symbolic)

    _latex = _pretty = _sympystr


# Alias for the class Variable.
Var = Variable


class OneVar(Variable):
    """Nondimensional number one.

    This is the identity element for the Product operator and the result
    of the Power operator when the zero exponent is given.
    """

    def __new__(cls):
        return super().__new__(cls)
    
    def __init__(self):
        super().__init__('')
        self._name = None
        self._symbolic = S.One

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbolic(self) -> Symbol:
        return self._symbolic

    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    @property
    def is_dependent(self) -> bool:
        return self._is_dependent
    
    @property
    def is_scaling(self) -> bool:
        return self._is_scaling


# class BasicCombinedVariable(Variable):
#     """Base class for combined variables.

#     A combined variable substitutes an object of the type BasicPower or
#     BasicProduct by a single variable with a simpler representation. All
#     properties of the original variable are preserved.
    
#     Parameters
#     ----------
#     variable : BasicVariable
#         The variable to be combined.
#     name : Optional[str], default=None
#         The name that represents the combined variable.

#     Attributes
#     ----------
#     name : Optional[str]
#         The name that will be displayed in symbolic expressions.
#     dimensions : dict[str, int]
#         Dictionary containing dimensions' names and exponents.
#     is_dependent : bool
#         If ``True``, the variable is dependent.
#     is_scaling : bool
#         If ``True``, the variable can be used as scaling parameter.
#     is_nondimensional : bool
#         If ``True``, the variable is nondimensional.

#     Methods
#     -------
#     uncombine()
#         Retuns the original variable.

#     Raises
#     ------
#     ValueError
#         If the variable is set as both dependent and scaling.
#     ValueError
#         If the variable is set as scaling, but with no dimensions.
#     """

#     def __init__(self, variable: Variable, name: Optional[str] = None):

#         name = name if name is not None else variable.name
        
#         self._variable: Variable = variable
#         super().__init__(
#             name=name,
#             dependent=variable.is_dependent,
#             scaling=variable.is_scaling,
#             **variable.dimensions,
#         )

#     # Redefining dimensions as a read-only property
#     @property
#     def dimensions(self) -> dict[str, int]:
#         return self._dimensions
    
#     def uncombine(self) -> Variable:
#         """Retuns the original variable."""

#         return self._variable

#     def __repr__(self) -> str:

#         class_name = type(self).__name__
#         variable_repr = _repr(self._variable)
#         if self.name == self._variable.name:
#             name_repr = ''
#         else:
#             name_repr = f", name='{self.name}'"

#         return (f'{class_name}('
#                 + variable_repr
#                 + name_repr
#                 + ')')


# class CombinedVariable(Variable, BasicCombinedVariable):
#     """Creates a symbolic combined variable.

#     A combined variable substitutes an object of the type Power or
#     Product by a single variable with a simpler representation. All
#     properties of the original variable are preserved.

#     Parameters
#     ----------
#     variable : BasicVariable
#         The variable to be combined.
#     name : Optional[str], default=None
#         The name that represents the combined variable.

#     Attributes
#     ----------
#     name : Optional[str]
#         The name that will be displayed in symbolic expressions.
#     dimensions : dict[str, int]
#         Dictionary containing dimensions' names and exponents.
#     is_dependent : bool
#         If ``True``, the variable is dependent.
#     is_scaling : bool
#         If ``True``, the variable can be used as scaling parameter.
#     is_nondimensional : bool
#         If ``True``, the variable is nondimensional.

#     Methods
#     -------
#     uncombine()
#         Retuns the original variable.

#     Raises
#     ------
#     ValueError
#         If the variable to be combined is given no name.
#     ValueError
#         If the variable is set as both dependent and scaling.
#     ValueError
#         If the variable is set as scaling, but with no dimensions.
#     """
    
#     def __new__(cls, variable: Variable, name: Optional[str] = None):

#         if name is None and variable.name is None:
#             raise ValueError("Variable to be combined has no name")
#         elif name is None:
#             name = variable.name

#         return super().__new__(cls, name)
    
#     def __init__(self, variable: Variable, name: Optional[str] = None):

#         BasicCombinedVariable.__init__(self, variable, name=name)

#     def _sympystr(self, printer) -> str:
#         """String representation according to Sympy."""

#         return printer._print_Symbol(self)
    
#     def _sympyrepr(self, printer) -> str:
#         """String representation according to Sympy."""

#         return BasicCombinedVariable.__repr__(self)

#     _latex = _pretty = _sympystr
