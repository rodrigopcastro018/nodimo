import pytest
from nodimo import Variable, DimensionalMatrix, ModelFunction, DimensionalModel


def test_variables():
    var1 = Variable('var1', d1=1, d2=-2, dependent=True)
    var2 = Variable('var2')
    var3 = Variable('var3', d1=-1, d2=1, scaling=True)
    var4 = Variable('var4', d1=3, d3=-5)
    var5 = Variable('var5', d1=0, d2=7)
    var6 = Variable('var6', d1=0, d3=0)
    var7 = Variable('var7', d2=1, scaling=True)

    dmodel1 = DimensionalModel(var1, var2, var3, var4, var5, var6, var7,
                               display_messages=False)

    dmodel2 = DimensionalModel(var1, var2, var3, var4, var5, var6, var7,
                               check_variables=False, display_messages=False)

    assert dmodel1.dimensional_variables == [var1, var5, var3, var7]
    assert dmodel1.nondimensional_variables == [var2, var6]
    assert dmodel1.scaling_variables == [var3, var7]
    assert dmodel1.nonscaling_variables == [var1, var5]

    assert dmodel2.dimensional_variables == [var1, var4, var5, var3, var7]
    assert dmodel2.nondimensional_variables == [var2, var6]
    assert dmodel2.scaling_variables == [var3, var7]
    assert dmodel2.nonscaling_variables == [var1, var4, var5]


def test_dimensions():
    var1 = Variable('var1', d1=2, d2=-1, dependent=True)
    var2 = Variable('var2', d1=1, d2=6)
    var3 = Variable('var3', d1=-5, d3=3, scaling=True)

    dmodel1 = DimensionalModel(var1, var2, var3, display_messages=False)
    dmodel2 = DimensionalModel(var1, var2, var3, check_variables=False,
                               display_messages=False)
    
    assert dmodel1.dimensions == ['d1', 'd2']
    assert dmodel2.dimensions == ['d1', 'd2', 'd3']


def test_dimensional_matrix():
    var1 = Variable('var1', d1=1, d2=-1, dependent=True)
    var2 = Variable('var2')
    var3 = Variable('var3', d1=3, d3=-4)
    var4 = Variable('var4', d1=-1, d2=2, scaling=True)
    var5 = Variable('var5', d1=0, d3=0)
    var6 = Variable('var6', d2=1, scaling=True)

    dmatrix = DimensionalMatrix(var1, var2, var4, var5, var6)
    dfunction = ModelFunction(var1, var2, var4, var5, var6, name='pi')

    dmodel = DimensionalModel(var1, var2, var3, var4, var5, var6,
                              display_messages=False)

    assert dmodel.dimensional_matrix.matrix == dmatrix.matrix[:2,:]
    assert dmodel.dimensional_function.function == dfunction.function


def test_model_creation():
    var1 = Variable('var1', d1=1, d2=-1, dependent=True)
    var2 = Variable('var2', d1=-1, d2=2, scaling=True)
    var3 = Variable('var3', d1=3, d3=-4)
    var4 = Variable('var4', d2=1, scaling=True)

    with pytest.raises(ValueError):
        dmodel1 = DimensionalModel()

    with pytest.raises(ValueError):
        dmodel2 = DimensionalModel(var1, var3, display_messages=False)
    
    with pytest.raises(ValueError):
        dmodel2 = DimensionalModel(var2, var3, var4, display_messages=False)


def test_dimensional_model_display(capfd):
    P = Variable('P', T=1, dependent=True)
    m = Variable('m', M=1)
    g = Variable('g', L=1, T=-2, scaling=True)
    R = Variable('R', L=1, scaling=True)
    t0 = Variable('theta0')
    dmodel = DimensionalModel(P, m, g, R, t0)

    dmodel.show()
    out, _ = capfd.readouterr()
    assert out == ('\x1b[93mVariables that can not be part of the model:\x1b[0m\n'
                   '\x1b[93m    m\x1b[0m\n'
                   '\x1b[93mDimensions that can not be part of the model:\x1b[0m\n'
                   '\x1b[93m    M\x1b[0m\n'
                   '\n'
                   'P = π(g, R, θ₀)\n'
                   '\n')
