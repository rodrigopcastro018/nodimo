"""This subpackage provides basic usage for variables.

Modules
-------
variable
    This module contains the class to create a variable.
group
    This module contains the class to create a group of variables.
matrix
    This module contains the class to create a dimensional matrix.
"""

from .variable import Variable, Var
from .group import VariableGroup, VarGroup
from .matrix import DimensionalMatrix, DimMatrix

__all__ = ['Variable', 'Var',
           'VariableGroup', 'VarGroup',
           'DimensionalMatrix', 'DimMatrix']