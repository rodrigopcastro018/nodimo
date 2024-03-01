from nodimo import Variable, VariableGroup
import sympy as sp
import pytest


def test_variables():
    var1 = Variable('var1', d1=1, d2=-1)
    var2 = Variable('var2', d1=-3, d3=2)
    var3 = Variable('var3')
    var4 = Variable('var4', d2=1, d3=-2)

    vars_list = [var1, var2, var3, var4]
    vars_tuple = (var1, var2, var3, var4)

    exponents_list = [2, 5, -3, -1]

    group1 = VariableGroup(vars_list, exponents_list)
    group2 = VariableGroup(vars_tuple, exponents_list)

    assert group1 == group2
    assert group1.variables == group2.variables

def test_exponents():
    var1 = Variable('var1', d1=1, d2=-1)
    var2 = Variable('var2', d1=-3, d3=2)
    var3 = Variable('var3')
    var4 = Variable('var4', d2=1, d3=-2)

    vars_list = [var1, var2, var3, var4]

    exponents_list = [2, 5, -3, -1]
    exponents_Matrix = sp.Matrix([exponents_list])

    group1 = VariableGroup(vars_list, exponents_list)
    group2 = VariableGroup(vars_list, exponents_Matrix)

    assert group1 == group2
    assert group1.exponents == group2.exponents

def test_exponents_type():
    var1 = Variable('var1', d1=-1, d2=2)
    var2 = Variable('var2')

    vars_list = [var1, var2]

    exponents_tuple = (-2, 3)

    with pytest.raises(TypeError):
        group = VariableGroup(vars_list, exponents_tuple)

def test_validation_of_variables():
    var = Variable('var', d1=1, d2=0)
    
    with pytest.raises(ValueError):
        group1 = VariableGroup([], [])
    
    with pytest.raises(ValueError):
        group2 = VariableGroup([var], [3])

def test_validation_of_exponents():
    var1 = Variable('var1', d1=0, d2=1)
    var2 = Variable('var2', d1=-2, d3=4)

    vars_list = [var1, var2]

    exponents_Matrix = sp.Matrix([-2, 3])

    with pytest.raises(ValueError):
        group = VariableGroup(vars_list, exponents_Matrix)

def test_validation_of_variables_and_exponents():
    pass