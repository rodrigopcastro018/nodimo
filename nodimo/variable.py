"""
=================================
Variable (:mod:`nodimo.variable`)
=================================

This module contains the class to create a symbolic variable.

Classes
-------
BasicVariable
    Base class for classes that represent variables.
Variable
    Creates a symbolic variable.
Classes
-------
VariableGroup
    Creates a product of variables, each raised to an exponent.
"""

import sympy as sp
from sympy import Symbol, Mul, Matrix
from typing import Union, Optional

from nodimo._internal import _obtain_dimensions, _build_dimensional_matrix


class BasicVariable:
    """Base class for classes that represent variables.

    Most basic type of variable, with a few attributes that are useful
    in describing its dimensional properties.

    Parameters
    ----------
    dependent : bool, default=False
        If ``True``, the variable is dependent.
    scaling : bool, default=False
        If ``True``, the variable can be used as scaling parameter.
    **dimensions : int
        The dimensions of the variable given as keyword arguments.

    Attributes
    ----------
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
        self, dependent: bool = False, scaling: bool = False, **dimensions: int
    ):

        self._dimensions: dict[str, int] = self._clear_null_dimensions(dimensions)
        self._is_dependent: bool = dependent
        self._is_scaling: bool = scaling
        self._is_nondimensional: bool = all(
            dim == 0 for dim in self._dimensions.values()
        )

        self._validate_properties()

    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dimensions: dict[str, int]):
        self._validate_properties(dimensions=dimensions)
        self._dimensions = self._clear_null_dimensions(dimensions)
        self._is_nondimensional = all(dim == 0 for dim in self._dimensions.values())

    @property
    def is_dependent(self) -> bool:
        return self._is_dependent

    @is_dependent.setter
    def is_dependent(self, dependent: bool):
        self._validate_properties(is_dependent=dependent)
        self._is_dependent = dependent

    @property
    def is_scaling(self) -> bool:
        return self._is_scaling

    @is_scaling.setter
    def is_scaling(self, scaling: bool):
        self._validate_properties(is_scaling=scaling)
        self._is_scaling = scaling

    @property
    def is_nondimensional(self) -> bool:
        return self._is_nondimensional

    def _clear_null_dimensions(self, dimensions: dict[str, int]):
        """Removes dimensions with exponent zero.

        Parameters
        ----------
        dimensions : dict[int]
            Raw dictionary with dimensions' names and exponents.

        Returns
        -------
        clear_dimensions : dict[int]
            Dictionary with null dimensions removed.
        """

        clear_dimensions = dimensions.copy()
        for dim, exp in dimensions.items():
            if exp == 0:
                del clear_dimensions[dim]

        return clear_dimensions

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


class Variable(BasicVariable, Symbol):
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

        super().__init__(dependent, scaling, **dimensions)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        name_repr = f"'{self.name}'"

        if self.is_nondimensional:
            dimensions_repr = ''
        else:
            dimensions = []

            for dim_name, dim_exp in self.dimensions.items():
                if dim_exp != 0:
                    dimensions.append(f'{dim_name}={dim_exp}')
            
            dimensions_repr = f", {', '.join(dimensions)}"
        
        dependent_repr = f', dependent=True' if self.is_dependent else ''
        scaling_repr = f', scaling=True' if self.is_scaling else ''

        return (f'{class_name}('
                + name_repr
                + dimensions_repr
                + dependent_repr
                + scaling_repr
                + ')')


# Alias for the class Variable.
Var = Variable


# Alias for type used in VariableGroup.
ListOrMatrix = Union[list, Matrix]


class VariableProduct(BasicVariable, Mul):
    """Creates a product of variables, each raised to an exponent.

    A VariableProduct consists of a product of variables, each raised to
    a particular exponent. The dimensional characteristics of this group
    of variables are evaluated and stored as attributes.

    Parameters
    ----------
    variables : list[Variable]
        List of variables that constitute the group.
    exponents : list or Matrix
        List or matrix containing each variable's exponent.
    check_inputs : bool, default=True
        If ``True``, variables and exponents are validated.

    Attributes
    ----------
    variables : list[Variable]
        List of variables that constitute the group.
    exponents : Matrix
        Matrix containing each variable's exponent.
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the group is dependent.
    is_nondimensional : bool
        If ``True``, the group is nondimensional.

    Raises
    ------
    TypeError
        If the type of ``exponents`` is not ``list`` or ``Matrix``.
    TypeError
        If the list of variables contains at least one not-Variable.
    ValueError
        If the number of different variables is lower than two.
    ValueError
        If the numbers of variables and exponents do not match.
    ValueError
        If the exponents are not in a row matrix.
        
    Examples
    --------
    Consider the dimensions mass ``M``, length ``L`` and time ``T``.
    Next, assuming that ``V`` is velocity, ``D`` is characteristic
    length, ``rho`` is density and ``mu`` is dynamic viscosity, the
    Reynolds number ``Re`` is built as:

    >>> from nodimo import Variable, VariableGroup
    >>> rho = Variable('rho', M=1, L=-3)
    >>> V = Variable('V', L=1, T=-1)
    >>> D = Variable('D', L=1)
    >>> mu = Variable('mu', M=1, L=-1, T=-1)
    >>> Re = VariableGroup([rho, V, D, mu], [1, 1, 1, -1])
    """

    def __new__(cls,
                variables: list[BasicVariable],
                exponents: ListOrMatrix,
                dependent: bool = False,
                scaling: bool = False):

        exponents = cls._convert_exponents(exponents)
        cls._validate_variables_and_exponents(variables, exponents)

        exponents_list = exponents.tolist()[0]
        terms = [var**exp for var, exp in zip(variables, exponents_list)]

        return super().__new__(cls, *terms)

    def __init__(self,
                 variables: list[BasicVariable],
                 exponents: ListOrMatrix,
                 dependent: bool = False,
                 scaling: bool = False):

        super().__init__()
        self.variables: list[BasicVariable] = list(variables)
        self.exponents: Matrix = self._convert_exponents(exponents)

        # If all variables are nondimensional, there is no need to
        # determine the dimensional properties.
        self._is_nondimensional = all(var.is_nondimensional
                                      for var in self.variables)
        
        if self.is_nondimensional:
            self.dimensions = dict()
        else:
            self._get_dimensions()
    
        self.is_dependent = dependent
        self.is_scaling = scaling        
    
    @classmethod
    def _convert_exponents(cls, exponents: ListOrMatrix) -> Matrix:
        """Converts a container of type ``list`` to the type ``Matrix``.

        Parameters
        ----------
        exponents : list or Matrix
            A container with numbers.

        Returns
        -------
        new_exponents: Matrix
            The ``exponents`` container converted to ``Matrix`` type. If
            the original container is already of the type ``Matrix``, no
            conversion is done and ``new_exponents`` is equal to
            ``exponents``.

        Raises
        ------
        TypeError
            If the type of ``exponents`` is not ``list`` or ``Matrix``.
        """

        if not isinstance(exponents, (list, Matrix)):
            raise TypeError("exponents type must be list or sympy.Matrix")

        if isinstance(exponents, list):
            new_exponents = sp.Matrix([exponents])
            new_exponents = sp.nsimplify(new_exponents,
                                         rational=True).as_mutable()
        else:
            new_exponents = exponents

        return new_exponents

    @classmethod
    def _validate_variables_and_exponents(cls,
                                          variables: list[BasicVariable],
                                          exponents: Matrix) -> None:
        """Validates provided variables and exponents.

        Parameters
        ----------
        variables: list[Variable]
            List of variables that constitute the group.
        exponents: Matrix
            List or matrix containing each variable's exponent.

        Raises
        ------
        TypeError
            If the list of variables contains at least one not-Variable.
        ValueError
            If the number of different variables is lower than two.
        ValueError
            If the numbers of variables and exponents do not match.
        ValueError
            If the exponents are not in a row matrix.
        """
        
        if not all(isinstance(var, BasicVariable) for var in variables):
            raise TypeError("All variables must be of type Variable")
        elif len(set(variables)) < 2:
            raise ValueError("Group must have at least two distinct variables")
        elif len(variables) != sp.Mul(*exponents.shape):
            raise ValueError("Number of variables and exponents must match")
        elif exponents.shape[0] != 1:
            raise ValueError("Exponents must be in a row matrix")

    def _get_dimensions(self) -> None:
        """Evaluates the dimensional properties of the group."""

        # First, get dimensions names.
        dimensions_names = _obtain_dimensions(*self.variables)

        # Second, get dimensions exponents.
        dimensional_matrix = _build_dimensional_matrix(self.variables,
                                                       dimensions_names)

        dimensions_exponents = dimensional_matrix * self.exponents.T

        # Third, combine names and exponents.
        self.dimensions = dict(zip(dimensions_names, dimensions_exponents))

    def _set_dependent_from_variables(self) -> None:
        """Set is_dependent property from component variables.

        The group is dependent if it contains a dependent variable with
        exponent.
        """

        is_dependent = [var.is_dependent for var in self.variables]
        has_exponent = list(map(bool, self.exponents.tolist()[0]))
        self.is_dependent = any(
            [dep and exp for (dep,exp) in zip(is_dependent, has_exponent)]
        )

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = f"[{', '.join(sp.srepr(var) for var in self.variables)}]"

        exponents_repr_list = []
        for e in self.exponents.tolist()[0]:
            if e.is_Integer or e.is_Rational:
                exponents_repr_list.append(str(e))
            else:
                exponents_repr_list.append(sp.srepr(e))

        exponents_repr = f", [{', '.join(exponents_repr_list)}]"
        dependent_repr = f', dependent=True' if self.is_dependent else ''
        scaling_repr = f', scaling=True' if self.is_scaling else ''

        return (f'{class_name}('
                + variables_repr
                + exponents_repr
                + dependent_repr
                + scaling_repr
                + ')')


# Alias for VariableGroup.
VarProduct = VariableProduct
