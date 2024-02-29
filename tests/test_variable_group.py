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