"""
=================================
Variable (:mod:`nodimo.variable`)
=================================

This module contains the class to create a variable.

Classes
-------
Variable
    Creates a symbolic variable.
"""

from sympy import Symbol
from nodimo.basic import BasicVariable


class Variable(BasicVariable, Symbol):
    """Creates a symbolic variable.

    It inherits from the sympy Symbol class the ability to be used in
    mathematical expressions.

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
            
            dimensions_repr = ', ' + ', '.join(dimensions)
        
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
