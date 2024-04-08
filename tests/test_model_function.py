import sympy as sp
import pytest
from nodimo import Variable, VariableGroup, ModelFunction


def test_dependent_and_independent_variables():
    var1 = Variable('var1', d1=1, d2=-2, dependent=True)
    var2 = Variable('var2', d1=0, d2=3, scaling=True)
    var3 = Variable('var3', d1=-1, d2=0)

    group1 = VariableGroup([var1, var2], [2, -1])
    group1._set_dependent_from_variables()
    group2 = VariableGroup([var2, var3], [-5, 3])
    group2._set_dependent_from_variables()

    function1 = ModelFunction(var1, var2, var3)
    function2 = ModelFunction(group1, group2, var2)

    assert function1.dependent_variable == var1
    assert function1.independent_variables == [var2, var3]
    assert function2.dependent_variable == group1
    assert function2.independent_variables == [group2, var2]


def test_function_creation():
    var1 = Variable('var1', d1=2, d2=3, dependent=True)
    var2 = Variable('var2', d1=0, dependent=True)
    var3 = Variable('var3', d1=-1, d2=0)
    var4 = Variable('var4', d1=3, scaling=True)

    group1 = VariableGroup([var1, var2], [-1, 2])
    group2 = VariableGroup([var2, var3], [3, 5])
    group3 = VariableGroup([var3, var4], [8, 7])

    with pytest.raises(ValueError):
        function1 = ModelFunction()

    with pytest.raises(ValueError):
        function2 = ModelFunction(var3)

    with pytest.raises(ValueError):
        function3 = ModelFunction(group3)

    with pytest.raises(ValueError):
        function4 = ModelFunction(var1, var2, var3)
    
    with pytest.raises(ValueError):
        function5 = ModelFunction(group1, group2)


def test_function_display(capfd):
    var1 = Variable('var1', d1=1, d2=-1)
    var2 = Variable('var2', d1=2, d2=-3, dependent=True)
    var3 = Variable('var3', d1=5, d2=-7)
    group = VariableGroup([var1, var3], [5,-1])

    mfunction = ModelFunction(var1, var2, group)

    mfunction.show()
    out, _ = capfd.readouterr()
    assert out == (''
                   '\n'
                   '        ⎛          5⎞\n'
                   '        ⎜      var₁ ⎟\n'
                   'var₂ = f⎜var₁, ─────⎟\n'
                   '        ⎝       var₃⎠\n'
                   '\n')


def test_model_function_repr():
    var1 = Variable('var1', d1=1, d2=-2, dependent=True)
    var2 = Variable('var2', d1=0, d2=3, scaling=True)
    var3 = Variable('var3', d1=-1, d2=0)

    group1 = VariableGroup([var1, var2], [2, -1])
    group1._set_dependent_from_variables()
    group2 = VariableGroup([var2, var3], [-5, 3])

    function1 = ModelFunction(var1, var2, var3)
    function2 = ModelFunction(group1, group2, var2)

    assert eval(sp.srepr(function1)) == function1
    assert eval(sp.srepr(function2)) == function2
