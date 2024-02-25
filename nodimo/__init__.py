"""Nodimo is a tool that creates nondimensional models.

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

Subpackages
-----------
variables
    This subpackage provides basic usage for variables.
models
    This subpackage provides the tools to build models.

Examples
--------
Free fall motion:
First, consider the dimensions mass (M), length (L) and time (T).
Second, assume that z is height, m is mass, v is velocity, g is
gravitational acceleration, t is time, z0 is the initial height and
v0 is the initial velocity. Third, take z as the dependent variable and
the initial set of scaling parameters formed by z0 and v0. The variables
are created as:
>>> from nodimo import Variable, NonDimModel, NonDimModels
>>> z = Variable('z', L=1, dependent=True)
>>> m = Variable('m', M=1)
>>> v = Variable('v', L=1, T=-1)
>>> g = Variable('g', L=1, T=-2)
>>> t = Variable('t', T=1)
>>> z0 = Variable('z_0', L=1, scaling=True)
>>> v0 = Variable('v_0', L=1, T=-1, scaling=True)

Next, the nondimensional model (ndmodel) for z can be built and
displayed as:
>>> ndmodel = NonDimModel(z, m, v, g, t, z0, v0)
>>> ndmodel.show()

If you also want to include g as one of the possible scaling parameters,
redefine it as scaling, and all nondimensional models (ndmodels) for z,
using the scaling parameters g, z0 and v0, can be built and revealed as:
>>> g = Variable('g', L=1, T=-2, scaling=True)
>>> ndmodels = NonDimModels(z, m, v, g, t, z0, v0)
>>> ndmodels.show()
"""

from .variables.variable import Variable, Var
from .variables.group import VariableGroup, VarGroup
from .variables.matrix import DimensionalMatrix, DimMatrix
from .models.function import ModelFunction
from .models.dimensional import DimensionalModel, DimModel
from .models.nondimensional import (NonDimensionalModel, NonDimModel,
                                    NonDimensionalModels, NonDimModels)
from sympy import init_printing

init_printing(root_notation=False)

__all__ = ['Variable', 'Var',
           'VariableGroup', 'VarGroup',
           'DimensionalMatrix', 'DimMatrix',
           'ModelFunction',
           'DimensionalModel', 'DimModel',
           'NonDimensionalModel', 'NonDimModel',
           'NonDimensionalModels', 'NonDimModels']