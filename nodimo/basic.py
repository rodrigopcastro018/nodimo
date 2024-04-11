"""
===========================
Basic (:mod:`nodimo.basic`)
===========================

This module contains base classes for Nodimo.

Classes
-------
BasicVariable
    Base class for classes that represent variables.
Basic
    Base class for classes created with variables.
"""

from sympy import srepr
from sympy.core._print_helpers import Printable
from typing import Optional

from nodimo._internal import (_show_object,
                              _remove_duplicates,
                              _obtain_dimensions)


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
    def dimensions(self, dimensions: dict[str, int]) -> None:
        self._validate_properties(dimensions=dimensions)
        self._dimensions = self._clear_null_dimensions(dimensions)
        self._is_nondimensional = all(dim == 0 for dim in self._dimensions.values())

    @property
    def is_dependent(self) -> bool:
        return self._is_dependent

    @is_dependent.setter
    def is_dependent(self, dependent: bool) -> None:
        self._validate_properties(is_dependent=dependent)
        self._is_dependent = dependent

    @property
    def is_scaling(self) -> bool:
        return self._is_scaling

    @is_scaling.setter
    def is_scaling(self, scaling: bool) -> None:
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
    ) -> None:
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


class Basic(Printable):
    """Base class for classes created with variables.

    This base class groups some common attributes and methods used by
    classes that are created with variables. It inherits from the Sympy
    Printable class the ability to display mathematical expressions in a
    pretty format.

    Parameters
    ----------
    *variables : Variable or VariableGroup
        Variables or groups that constitute the Basic class.

    Attributes
    ----------
    variables : list[Variable or VariableGroup]
        List of variables used.
    dimensions : list[str]
        List with dimensions' names of the given variables.
    """

    def __init__(self, *variables: BasicVariable):

        self.variables: list[BasicVariable] = _remove_duplicates(list(variables))
        self.dimensions: list[str] = _obtain_dimensions(*variables)
    
    def show(self) -> None:
        """Displays the object in pretty format."""

        _show_object(self)

    def __eq__(self, other) -> bool:

        if self is other:
            return True
        elif not isinstance(other, type(self)):
            return False
        elif set(self.variables) != set(other.variables):
            return False
        
        return True
    
    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return "'_sympystr' method not implemented yet"

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join([srepr(var) for var in self.variables])

        return (f'{class_name}('
                + variables_repr
                + ')')

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return R"\text{\textit{\_latex} method not implemented yet}"
