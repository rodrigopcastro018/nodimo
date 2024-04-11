import sympy as sp
from nodimo import Variable, VariableGroup
from nodimo._internal import (_is_running_on_jupyter,
                              _show_object,
                              _print_horizontal_line,
                              _obtain_dimensions,
                              _build_dimensional_matrix)


def test_environment():
    assert not _is_running_on_jupyter


def test_show_object(capfd):
    var1 = Variable('var1', d1=1, d2=2, dependent=True)
    var2 = Variable('var2', d1=-2, d2=3)
    group = VariableGroup([var1, var2], [-2,3])

    _show_object(var1)
    out_var1, _ = capfd.readouterr()

    _show_object(group)
    out_group, _ = capfd.readouterr()

    assert out_var1 == '\nvar₁\n\n'
    assert out_group == ('\n'
                         '    3\n'
                         'var₂ \n'
                         '─────\n'
                         '    2\n'
                         'var₁ \n'
                         '\n')


def test_horizontal_line(capfd):
    _print_horizontal_line()
    out, _ = capfd.readouterr()

    assert out == 78 * '-' + '\n'


def test_obtain_dimensions():
    var1 = Variable('var1', d1=3, e1=-1, scaling=True)
    var2 = Variable('var2', e2=0, d2=10, dependent=True)
    var3 = Variable('var3', c2=0, d2=2, d3=1)
    var4 = Variable('var4', c1=0)

    group = VariableGroup([var1, var2, var3, var4], [0, 1, -13, 5])

    dimensions1 = _obtain_dimensions(var1, var2, var3, var4)
    dimensions2 = _obtain_dimensions(group)
    dimensions3 = _obtain_dimensions(group, var3, var1, var2, var4)

    assert dimensions1 == ['d1', 'e1', 'd2', 'd3']
    assert dimensions2 == ['d2', 'd3']
    assert dimensions3 == ['d2', 'd3', 'd1', 'e1']


def test_build_dimensional_matrix():
    var1 = Variable('var1', d1=1, c1=2, scaling=True)
    var2 = Variable('var2', c2=3, d2=4, dependent=True)
    var3 = Variable('var3', e2=5, d2=6, e1=7)
    var4 = Variable('var4', e1=8)

    group = VariableGroup([var1, var2, var3, var4], [1, 1, 1, 1])

    matrix1 = _build_dimensional_matrix([var1, var2, var3, var4])
    expected_matrix1 = sp.Matrix([[1, 0, 0, 0],
                                  [2, 0, 0, 0],
                                  [0, 3, 0, 0],
                                  [0, 4, 6, 0],
                                  [0, 0, 5, 0],
                                  [0, 0, 7, 8]])

    matrix2 = _build_dimensional_matrix([group])
    expected_matrix2 = sp.Matrix([[1 ],
                                  [2 ],
                                  [3 ],
                                  [10],
                                  [5 ],
                                  [15]])
        
    assert matrix1 == expected_matrix1
    assert matrix2 == expected_matrix2