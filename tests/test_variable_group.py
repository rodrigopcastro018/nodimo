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
    assert isinstance(group1.exponents, sp.Matrix)
    assert isinstance(group2.exponents, sp.Matrix)

def test_exponents_type():
    var1 = Variable('var1', d1=-1, d2=2)
    var2 = Variable('var2')

    vars_list = [var1, var2]

    exponents_tuple = (-2, 3)

    with pytest.raises(TypeError):
        group = VariableGroup(vars_list, exponents_tuple)

def test_validation_of_variables():
    var = Variable('var', d1=1, d2=0)

    with pytest.raises(TypeError):
        group1 = VariableGroup([1], [])

    with pytest.raises(ValueError):
        group2 = VariableGroup([], [])
    
    with pytest.raises(ValueError):
        group3 = VariableGroup([var], [3])

def test_validation_of_exponents():
    var1 = Variable('var1', d1=0, d2=1)
    var2 = Variable('var2', d1=-2, d3=4)

    vars_list = [var1, var2]

    exponents_Matrix = sp.Matrix([-2, 3])

    with pytest.raises(ValueError):
        group = VariableGroup(vars_list, exponents_Matrix)

def test_validation_of_variables_and_exponents():
    var1 = Variable('var1', d1=0, d2=-2)
    var2 = Variable('var2', d1=1, d2=3)
    var3 = Variable('var3', d1=-1, d3=2)

    with pytest.raises(ValueError):
        group1 = VariableGroup([var1, var2], [])
    
    with pytest.raises(ValueError):
        group2 = VariableGroup([var1, var2], [1, -1, 10])
    
    with pytest.raises(ValueError):
        group3 = VariableGroup([var1, var2, var3], [-2, 3])


def test_dependent():
    var1 = Variable('var1', d1=0, d2=0, d3=0, dependent=True)
    var2 = Variable('var2', d1=1, d2=1)
    var3 = Variable('var3', d2=3, d3=-1)

    group1 = VariableGroup([var2, var3], [-10, 15])
    group2 = VariableGroup([var1, var2, var3], [1, 5, -1])
    group3 = VariableGroup([var1, var1, var2, var3], [3, -2, -1, 6])

    assert not group1.is_dependent
    assert group2.is_dependent
    assert group3.is_dependent


def test_dimensions():
    var1 = Variable('var1', d1=11, d2=-5, d3=7)
    var2 = Variable('var2', d1=2, d4=3)
    var3 = Variable('var3')

    group1 = VariableGroup([var1, var2], [1, 1])
    group2 = VariableGroup([var2, var3], [3, 2])
    group3 = VariableGroup([var1, var2, var3], [-1, 2, -3])
    group4 = VariableGroup([var1, var2], [1, 2], check_dimensions=False)

    assert group1.dimensions == {'d1':13, 'd2':-5, 'd3':7, 'd4':3}
    assert group2.dimensions == {'d1':6, 'd4':9}
    assert group3.dimensions == {'d1':-7, 'd2':5, 'd3':-7, 'd4':6}
    assert group4.dimensions == {}


def test_nondimensional():
    var1 = Variable('var1', d1=1, d2=-3, d3=0)
    var2 = Variable('var2', d1=0, d2=1, d3=-1)
    var3 = Variable('var3', d1=0, d2=1, d3=0)
    var4 = Variable('var4', d1=1, d2=-1, d3=-1)
    var5 = Variable('var5')
    var6 = Variable('var6', d1=0, d3=0)
    var7 = Variable('var7', d1=0)
    
    group1 = VariableGroup([var1, var2, var3, var4], [1, 1, 1, -1])
    group2 = VariableGroup([var1, var2, var3, var4, var5], [1, 1, 1, -1, 1])
    group3 = VariableGroup([var5, var6, var7], [-1, 2, -3])
    group4 = VariableGroup([var5, var6, var7], [-1, 2, -3],
                           check_dimensions=False)
    group5 = VariableGroup([var1, var2, var3], [1, 1, 1])
    group6 = VariableGroup([var1, var2, var3, var5], [1, 1, 1, -9])

    assert group1.is_nondimensional
    assert group2.is_nondimensional
    assert group3.is_nondimensional
    assert group4.is_nondimensional
    assert not group5.is_nondimensional
    assert not group6.is_nondimensional