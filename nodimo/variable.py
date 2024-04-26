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

from sympy import Symbol
from sympy.core.numbers import One
from typing import Optional

from nodimo._internal import _sympify_number, _repr


class BasicVariable:
    """Base class for variables.

    Most basic type of variable, with a few attributes that are useful
    in describing its dimensional properties.

    Parameters
    ----------
    name : Optional[str], default=None
        The name that will be displayed in symbolic expressions.
    dependent : bool, default=False
        If ``True``, the variable is dependent.
    scaling : bool, default=False
        If ``True``, the variable can be used as scaling parameter.
    **dimensions : int
        The dimensions of the variable given as keyword arguments.

    Attributes
    ----------
    name : Optional[str]
        The name that will be displayed in symbolic expressions.
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
        name: Optional[str] = None,  # TODO: Turn name attribute mandatory. Keep it optional on Product and Power.
        dependent: bool = False,
        scaling: bool = False,
        **dimensions: int,
    ):

        self.name: Optional[str] = name
        self._dimensions: dict[str, int] = dimensions
        self._is_dependent: bool = bool(dependent)
        self._is_scaling: bool = bool(scaling)
        self._is_nondimensional: bool = all(
            dim == 0 for dim in self._dimensions.values()
        )

        self._validate_properties()
        self._sympify_exponents()
        self._clear_null_dimensions()

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

    def __eq__(self, other) -> bool:  # TODO: Implement this method for all childs of this class

        if self is other:
            return True
        elif not isinstance(other, type(self)):
            return False
        elif self.name != other.name:
            return False
        elif self._is_dependent and not other.is_dependent:
            return False
        elif self._is_scaling and not other.is_scaling:
            return False
        elif self._is_nondimensional and not other.is_nondimensional:
            return False
        elif self._dimensions != other.dimensions:
            return False

        return True

    def __hash__(self) -> int:  # TODO: Create hash method

        pass

    def __str__(self) -> str:

        return self.name

    def __repr__(self) -> str:

        class_name = type(self).__name__
        name_repr = f"'{self.name}'" if self.name is not None else ''

        if self._is_nondimensional:
            dimensions_repr = ''
        else:
            dimensions = []
            for dim_name, dim_exp in self.dimensions.items():
                dimensions.append(f'{dim_name}={dim_exp}')
            dimensions_repr = f", {', '.join(dimensions)}"
        
        dependent_repr = f', dependent=True' if self._is_dependent else ''
        scaling_repr = f', scaling=True' if self._is_scaling else ''

        return (f'{class_name}('
                + name_repr
                + dimensions_repr
                + dependent_repr
                + scaling_repr
                + ')')


class Variable(Symbol, BasicVariable):
    """Creates a symbolic variable.

    This class inherits the dimensional properties of BasicVariable and
    adds to it, by inheriting from sympy.Symbol, the ability to be used
    in symbolic mathematical expressions.

    Parameters  
    ----------
    name : str
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

    Examples
    --------
    Considering the dimensions mass ``M``, length ``L`` and time ``T``,
    a force ``F`` can be defined as:

    >>> from nodimo import Variable
    >>> F = Variable('F', M=1, L=1, T=-2)

    To define a nondimensional variable ``A`` is sufficient to provide
    just its name:

    >>> A = Variable('A')

    To use a greek letter in symbolic expressions, just provide its
    english representation as the name of the variable:

    >>> a = Variable('alpha')
    """

    # See issue #32 before removing this method.
    def __new__(cls,
                name: str,
                dependent: bool = False,
                scaling: bool = False,
                 **dimensions: int):
        
        return super().__new__(cls, name)

    def __init__(self,
                 name: str,
                 dependent: bool = False,
                 scaling: bool = False,
                 **dimensions: int):

        super().__init__(name=name, dependent=dependent, scaling=scaling, **dimensions)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        return BasicVariable.__repr__(self)


# Alias for the class Variable.
Var = Variable


class OneVar(BasicVariable, One):
    """Nondimensional number one.

    This is the identity element for the Product operator and the result
    of the Power operator when the zero exponent is given.
    """

    def __init__(self):
        super().__init__()

    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    @property
    def is_dependent(self) -> bool:
        return self._is_dependent
    
    @property
    def is_scaling(self) -> bool:
        return self._is_scaling


class BasicCombinedVariable(BasicVariable):
    """Base class for combined variables.

    A combined variable substitutes an object of the type BasicPower or
    BasicProduct by a single variable with a simpler representation. All
    properties of the original variable are preserved.
    
    Parameters
    ----------
    variable : BasicVariable
        The variable to be combined.
    name : Optional[str], default=None
        The name that represents the combined variable.

    Attributes
    ----------
    name : Optional[str]
        The name that will be displayed in symbolic expressions.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the variable is dependent.
    is_scaling : bool
        If ``True``, the variable can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the variable is nondimensional.

    Methods
    -------
    uncombine()
        Retuns the original variable.

    Raises
    ------
    ValueError
        If the variable is set as both dependent and scaling.
    ValueError
        If the variable is set as scaling, but with no dimensions.
    """

    def __init__(self, variable: BasicVariable, name: Optional[str] = None):

        name = name if name is not None else variable.name
        
        self._variable: BasicVariable = variable
        super().__init__(
            name=name,
            dependent=variable.is_dependent,
            scaling=variable.is_scaling,
            **variable.dimensions,
        )

    # Redefining dimensions as a read-only property
    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions
    
    def uncombine(self) -> BasicVariable:
        """Retuns the original variable."""

        return self._variable

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variable_repr = _repr(self._variable)
        if self.name == self._variable.name:
            name_repr = ''
        else:
            name_repr = f", name='{self.name}'"

        return (f'{class_name}('
                + variable_repr
                + name_repr
                + ')')


class CombinedVariable(Variable, BasicCombinedVariable):
    """Creates a symbolic combined variable.

    A combined variable substitutes an object of the type Power or
    Product by a single variable with a simpler representation. All
    properties of the original variable are preserved.

    Parameters
    ----------
    variable : BasicVariable
        The variable to be combined.
    name : Optional[str], default=None
        The name that represents the combined variable.

    Attributes
    ----------
    name : Optional[str]
        The name that will be displayed in symbolic expressions.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the variable is dependent.
    is_scaling : bool
        If ``True``, the variable can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the variable is nondimensional.

    Methods
    -------
    uncombine()
        Retuns the original variable.

    Raises
    ------
    ValueError
        If the variable to be combined is given no name.
    ValueError
        If the variable is set as both dependent and scaling.
    ValueError
        If the variable is set as scaling, but with no dimensions.
    """
    
    def __new__(cls, variable: BasicVariable, name: Optional[str] = None):

        if name is None and variable.name is None:
            raise ValueError("Variable to be combined has no name")
        elif name is None:
            name = variable.name

        return super().__new__(cls, name)
    
    def __init__(self, variable: BasicVariable, name: Optional[str] = None):

        BasicCombinedVariable.__init__(self, variable, name=name)

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return printer._print_Symbol(self)
    
    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        return BasicCombinedVariable.__repr__(self)

    _latex = _pretty = _sympystr
