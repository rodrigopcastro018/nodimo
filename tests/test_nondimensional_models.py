import pytest
from nodimo import Variable, NonDimensionalModel, NonDimensionalModels


def test_scaling_variables():
    z = Variable('z', L=1, dependent=True)
    m = Variable('m', M=1)
    v = Variable('v', L=1, T=-1)
    g = Variable('g', L=1, T=-2, scaling=True)
    t = Variable('t', T=1)
    z0 = Variable('z_0', L=1)
    v0 = Variable('v_0', L=1, T=-1)

    with pytest.raises(ValueError):
        ndmodels = NonDimensionalModels(z, m, v, g, t, z0, v0,
                                        display_messages=False)


def test_scaling_groups():
    z = Variable('z', L=1, dependent=True)
    m = Variable('m', M=1)
    v = Variable('v', L=1, T=-1)
    g = Variable('g', L=1, T=-2, scaling=True)
    t = Variable('t', T=1)
    z0 = Variable('z_0', L=1, scaling=True)
    v0 = Variable('v_0', L=1, T=-1, scaling=True)

    ndmodels1 = NonDimensionalModels(z, m, v, g, t, z0, v0,
                                     display_messages=False)

    g.is_scaling, z0.is_scaling, v0.is_scaling = (False, False, False)

    ndmodels2 = NonDimensionalModels(z, m, v, g, t, z0, v0,
                                     display_messages=False)

    scaling_groups1 = [[g, z0], [g, v0], [z0, v0]]
    scaling_groups2 = [[v, g], [v, t], [v, z0], [g, t], [g, z0],
                       [g, v0], [t, z0], [t, v0], [z0, v0]]

    assert ndmodels1.scaling_groups == scaling_groups1
    assert ndmodels2.scaling_groups == scaling_groups2


def test_nondimensional_models():
    z = Variable('z', L=1, dependent=True)
    m = Variable('m', M=1)
    v = Variable('v', L=1, T=-1)
    t = Variable('t', T=1)
    g = Variable('g', L=1, T=-2, scaling=True)
    z0 = Variable('z_0', L=1, scaling=True)
    v0 = Variable('v_0', L=1, T=-1, scaling=False)

    ndmodel1 = NonDimensionalModel(z, m, v, t, g, z0, v0,
                                   display_messages=False)

    z0.is_scaling, v0.is_scaling = (False, True)
    ndmodel2 = NonDimensionalModel(z, m, v, t, g, z0, v0,
                                   display_messages=False)

    g.is_scaling, z0.is_scaling = (False, True)
    ndmodel3 = NonDimensionalModel(z, m, v, t, g, z0, v0,
                                   display_messages=False)

    ndfunctions = [ndmodel1.nondimensional_function,
                   ndmodel2.nondimensional_function,
                   ndmodel3.nondimensional_function]

    g.is_scaling = True
    ndmodels = NonDimensionalModels(z, m, v, t, g, z0, v0,
                                    display_messages=False)

    assert ndmodels.nondimensional_functions == ndfunctions
