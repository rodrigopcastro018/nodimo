#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io
#                    ASCII Art (Font Tmplr) by https://patorjk.com

"""
Nodimo
======

Nodimo is a tool that creates dimensionless models.

The main purpose of Nodimo is to transform a dimensional relationship
between quantities into a dimensionless one. This is done by grouping
dimensional quantities into dimensionless products in such a way that
the resulting number of products is always lower than or equal to the
starting number of quantities. Therefore, the ensuing dimensionless
model is, at the same time, a generalization and simplification of the
dimensional model.

Nodimo supports any number of dimensions and quantities. It can be used
for applications in science, engineering, economics and finance. The
resulting dimensionless relations can be used as the basis for further
studies in similarity and model testing.

Notes
-----
The use of Nodimo requires basic knowledge of dimensional analysis,
specially on choosing the appropriate set of scaling parameters and
indentifying established dimensionless groups. It is recommended the
use of IPython/Jupyter for a better displaying of the results.

Modules
-------
dimension
    This module contains the class to create a quantity dimension.
quantity
    This module contains the class to create a quantity.
power
    This module contains the class to create a power of a quantity.
product
    This module contains the class to create a product of quantities.
collection
    This module contains the base class for everything that is created
    with a collection of quantities.
groups
    This module contains classes to create groups of quantities, which
    are specific types of collections.
matrix
    This module contains the class to create a dimensional matrix.
relation
    This module contains the class to create a relation between
    quantities.
model
    This module contains the classes to create (non)dimensional models.
"""

from nodimo.quantity import Quantity, Q
from nodimo.power import Power
from nodimo.product import Product
from nodimo.matrix import DimensionalMatrix
from nodimo.relation import Relation
from nodimo.model import Model

__all__ = [
    'Quantity',
    'Q',
    'Power',
    'Product',
    'DimensionalMatrix',
    'Relation',
    'Model',
]
