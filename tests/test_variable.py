from nodimo import Variable
import pytest


def test_name():
    var = Variable('var')
    assert var.name == 'var'


def test_dimensions():
    # Dimensional variables
    dvar1 = Variable('dvar1', d1=0, d2=0, d3=0, d4=0, d5=1)
    dvar2 = Variable('dvar2', d1=0, d2=0, d3=0, d4=0, d5=1.5)

    # Nondimenisonal variables
    ndvar1 = Variable('ndvar1')
    ndvar2 = Variable('ndvar2', d1=0, d2=0, d3=0, d4=0, d5=0)
    ndvar3 = Variable('ndvar3', d1=0.0, d2=0.0, d3=0.0, d4=0.0, d5=0.0)

    assert not dvar1.is_nondimensional
    assert not dvar2.is_nondimensional
    assert ndvar1.is_nondimensional
    assert ndvar2.is_nondimensional
    assert ndvar3.is_nondimensional


def test_dependent():
    var1 = Variable('var1', d1=0, d2=1, dependent=True)
    var2 = Variable('var2', d1=2, d2=-1, dependent=False)
    var3 = Variable('var3', d1=2, d2=-1)

    assert var1.is_dependent
    assert not var2.is_dependent
    assert not var3.is_dependent


def test_scaling():
    var1 = Variable('var1', d1=1, scaling=True)
    var2 = Variable('var2', d1=-1, scaling=False)
    var3 = Variable('var3', d1=3)

    assert var1.is_scaling
    assert not var2.is_scaling
    assert not var3.is_scaling


def test_dependent_and_scaling():
    with pytest.raises(ValueError):
        var = Variable('var', d1=0.1, dependent=True, scaling=True)


def test_scaling_and_nondimensional():
    with pytest.raises(ValueError):
        var = Variable('var', scaling=True)
