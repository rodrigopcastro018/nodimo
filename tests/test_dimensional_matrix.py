import sys
import sympy as sp
from nodimo import Variable, VariableGroup, DimensionalMatrix


def test_variables():
    var1 = Variable('var1', d1=1, d2=-2, dependent=True)
    var2 = Variable('var2', d1=-1, scaling=False)

    group = VariableGroup([var1, var2], [-1, 2])

    dmatrix1 = DimensionalMatrix(var1, var2)
    dmatrix2 = DimensionalMatrix(var1, group)

    assert dmatrix1.variables == [var1, var2]
    assert dmatrix2.variables == [var1, group]


def test_dimensions():
    var1 = Variable('var1', d1=3, d2=0)
    var2 = Variable('var2', d1=4, d2=1, scaling=False)

    group = VariableGroup([var1, var2], [3, 1])

    dmatrix1 = DimensionalMatrix(var1, var2)
    dmatrix2 = DimensionalMatrix(var1, var2, dimensions=['d1', 'd2'])
    dmatrix3 = DimensionalMatrix(var1, var2, dimensions=['d2'])
    dmatrix4 = DimensionalMatrix(var2, group)

    assert dmatrix1.dimensions == ['d1', 'd2']
    assert dmatrix2.dimensions == ['d1', 'd2']
    assert dmatrix1.matrix[1,:] == dmatrix3.matrix
    assert dmatrix4.dimensions == ['d1', 'd2']



def test_matrix():
    var1 = Variable('var1', d1=6, d2=5, scaling=True)
    var2 = Variable('var2', d1=-3, d2=-1, scaling=False)

    group = VariableGroup([var1, var2], [1, 1])

    matrix1 = sp.Matrix([[6, -3],
                         [5, -1]])

    matrix2 = sp.Matrix([[3],
                         [4]])

    dmatrix1 = DimensionalMatrix(var1, var2)
    dmatrix2 = DimensionalMatrix(group)

    assert dmatrix1.matrix == matrix1
    assert dmatrix2.matrix == matrix2


def test_labeled_matrix():
    var1 = Variable('var1', d1=5, d2=-2, scaling=True)
    var2 = Variable('var2', d1=7, d2=3, scaling=False)

    labeled_matrix = sp.Matrix([[Variable(''), var1, var2],
                                [        'd1',    5,    7],
                                [        'd2',   -2,    3]])
    
    dmatrix = DimensionalMatrix(var1, var2)

    assert dmatrix.labeled_matrix == labeled_matrix


def test_rank():
    var1 = Variable('var1', d1=1, d2=0, d3=0, d4=0)
    var2 = Variable('var2', d1=0, d2=1, d3=0, d4=0)
    var3 = Variable('var3', d1=0, d2=0, d3=1, d4=0)
    var4 = Variable('var4', d1=0, d2=0, d3=0, d4=1)
    var5 = Variable('var5', d1=1, d2=0, d3=1, d4=0)
    var6 = Variable('var6', d1=0, d2=1, d3=0, d4=1)

    dmatrix1 = DimensionalMatrix()
    dmatrix2 = DimensionalMatrix(var1)
    dmatrix3 = DimensionalMatrix(var1, var2)
    dmatrix4 = DimensionalMatrix(var1, var2, var3)
    dmatrix5 = DimensionalMatrix(var1, var2, var3, var4)
    dmatrix6 = DimensionalMatrix(var1, var2, var3, var4, var5)
    dmatrix7 = DimensionalMatrix(var1, var2, var3, var4, var5, var6)

    assert dmatrix1.rank == 0
    assert dmatrix2.rank == 1
    assert dmatrix3.rank == 2
    assert dmatrix4.rank == 3
    assert dmatrix5.rank == 4
    assert dmatrix6.rank == 4
    assert dmatrix7.rank == 4


def test_matrix_display(capfd):
    var1 = Variable('var1', d1=-1, d2=3)
    var2 = Variable('var2', d1=4, d2=-2, dependent=True)
    dmatrix = DimensionalMatrix(var1, var2)

    dmatrix.show()
    out, _ = capfd.readouterr()
    assert out == ('\n'
                   '⎡    var₁  var₂⎤\n'
                   '⎢              ⎥\n'
                   '⎢d₁   -1    4  ⎥\n'
                   '⎢              ⎥\n'
                   '⎣d₂   3     -2 ⎦\n'
                   '\n')
