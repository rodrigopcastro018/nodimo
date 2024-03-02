import pytest
from nodimo import Variable, VariableGroup, ModelFunction, NonDimensionalModel


def test_validation_of_scaling_variables():
    var1 = Variable('var1', d1= 1, d2= 0, d3= 0, scaling=True)
    var2 = Variable('var2', d1=-1, d2= 3, d3= 0, dependent=True)
    var3 = Variable('var3', d1= 0, d2= 1, d3= 1)
    var4 = Variable('var4', d1= 1, d2=-1, d3=-2, scaling=True)
    var5 = Variable('var5', d1= 2, d2=-1, d3=-2, scaling=True)

    with pytest.raises(ValueError):
        ndmodel1 = NonDimensionalModel(var1, var3)

    with pytest.raises(ValueError):
        ndmodel2 = NonDimensionalModel(var1, var2)

    with pytest.raises(ValueError):
        ndmodel3 = NonDimensionalModel(var1, var2, var3)

    with pytest.raises(ValueError):
        ndmodel4 = NonDimensionalModel(var1, var2, var3, var4)

    with pytest.raises(ValueError):
        ndmodel5 = NonDimensionalModel(var1, var2, var3, var4, var5)


def test_nondimensional_model():
    F = Variable('F', M=1, L=1, T=-2, dependent=True)
    rho = Variable('rho', M=1, L=-3, T=0, scaling=True)
    U = Variable('U', M=0, L=1, T=-1, scaling=True)
    mu = Variable('mu', M=1, L=-1, T=-1)
    D = Variable('D', M=0, L=1, T=0, scaling=True)

    ndmodel = NonDimensionalModel(F, rho, U, mu, D)

    group1 = VariableGroup([F, mu, rho, U, D], [1, 0, -1, -2, -2])
    group2 = VariableGroup([F, mu, rho, U, D], [0, 1, -1, -1, -1])

    ndfunction = ModelFunction(group1, group2, name='Pi')
    
    assert ndmodel.nondimensional_groups == [group1, group2]
    assert ndmodel.nondimensional_function == ndfunction


def test_check_of_scaling_variables():
    pass


def test_build_of_nondimensional_model():
    pass
