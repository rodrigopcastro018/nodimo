#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io
#                    ASCII Art (Font Tmplr) by https://patorjk.com

"""
Nodimo
======

Nodimo is a tool that creates nondimensional models.

The main purpose of Nodimo is to transform a dimensional relationship
between variables into a nondimensional one. The variables are gathered
in nondimensional groups such that the number of groups is lower than
the number of variables. The resulting nondimensional model is, at the
same time, a generalization and simplification of the dimensional model.

Nodimo supports any number of dimensions and variables. It can be used
for applications in science, engineering, economics and finance. The
resulting nondimensional groups can be used as the basis for further
studies in similarity and model testing.

Notes
-----
The use of this package requires basic knowledge of dimensional
analysis, specially on choosing the appropriate set of scaling
parameters and indentifying established nondimensional groups.

Modules
-------
variable
    This module contains the class to create a variable.
power
    This module contains the class to create a power of a variable.
product
    This module contains the class to create a product of variables.
collection
    This module contains the base class for everything that is created
    with a collection of variables.
groups
    This module contains classes to create groups of variables, which
    are specific types of collections.
matrix
    This module contains the class to create a dimensional matrix.
relation
    This module contains the class to create a relation between
    variables.
model
    This module contains the classes to create (non)dimensional models.
"""

# from sympy import init_printing

from nodimo.variable import Variable, Var
from nodimo.power import Power
from nodimo.product import Product, Prod
from nodimo.matrix import DimensionalMatrix, DimMatrix
from nodimo.relation import Relation
from nodimo.model import Model

# init_printing(root_notation=False)

__all__ = ['Variable', 'Var', 'Power', 'Product', 'Prod',
           'DimensionalMatrix', 'DimMatrix', 'Relation', 'Model']

"""To include in global settings:
    - root_notation
    - warnings display
"""