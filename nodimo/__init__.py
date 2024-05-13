"""
======
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
group
    This module contains the class to create a group of variables.
matrix
    This module contains the class to create a dimensional matrix.
function
    This module contains the class to creates model functions.
dimensional
    This module contains the class to create a dimensional model.
nondimensional
    This module contains the classes to create nondimensional models.

Examples
--------
* Free fall

Consider the dimensions mass ``M``, length ``L`` and time ``T``. Next,
assume that ``z`` is height, ``m`` is mass, ``v`` is velocity, ``g`` is
gravitational acceleration, ``t`` is time, ``z0`` is the initial height
and ``v0`` is the initial velocity. In addition, take the initial set of
scaling parameters formed by ``z0`` and ``v0``. The variables are
created as:

>>> from nodimo import Variable, NonDimModel, NonDimModels
>>> z = Variable('z', L=1, dependent=True)
>>> m = Variable('m', M=1)
>>> v = Variable('v', L=1, T=-1)
>>> g = Variable('g', L=1, T=-2)
>>> t = Variable('t', T=1)
>>> z0 = Variable('z_0', L=1, scaling=True)
>>> v0 = Variable('v_0', L=1, T=-1, scaling=True)

Next, the nondimensional model ``ndmodel`` for ``z`` can be built and
displayed as:

>>> ndmodel = NonDimModel(z, m, v, g, t, z0, v0)
>>> ndmodel.show()

If you also want to include ``g`` as one of the possible scaling
parameters, redefine it as scaling, and all nondimensional models
``ndmodels`` for ``z`` can be built and revealed as:

>>> g.is_scaling = True
>>> ndmodels = NonDimModels(z, m, v, g, t, z0, v0)
>>> ndmodels.show()
"""

# from sympy import init_printing

from nodimo.variable import Variable, Var
from nodimo.product import Product, Prod
from nodimo.power import Power
from nodimo.matrix import DimensionalMatrix, DimMatrix
from nodimo.model import Model

# init_printing(root_notation=False)

__all__ = ['Variable', 'Var',
           'Product', 'Prod',
           'Power', 'Pow',
           'DimensionalMatrix', 'DimMatrix',
           'Relation',
           'Model']

"""To include in global settings:
    - limit_denominator
    - root_notation
    - warnings?
"""