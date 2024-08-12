from sympy import srepr, latex, pretty, S, sympify, ImmutableDenseMatrix
from pytest import raises
from warnings import catch_warnings
from nodimo.quantity import Quantity, Constant, One
from nodimo.product import Product
from nodimo.power import Power
from nodimo.collection import Collection
from nodimo._internal import NodimoWarning


def test_quantities_and_dimensions():
    a = Quantity('a', A=2, B=3, C=5, scaling=True)
    b = Constant('b')
    c = Power(a, -2, dependent=True)
    d = Product(a, b, c, Constant(1/5))
    e = One()
    col1 = Collection(a, b, c, d, e)
    col2 = Collection(b, e, Constant(7))

    assert col1.quantities == [a, b, c, d, e]
    assert col1._dimensions == dict(A=S.NaN, B=S.NaN, C=S.NaN)
    assert not col1._is_dimensionless
    assert col2._is_dimensionless


def test_disassembled_quantities():
    a = Quantity('a', A=2, B=3, C=5, scaling=True)
    b = Constant('b')
    c = Power(a, -2, dependent=True)
    d = Constant(1/5)
    e = Product(a, b, c, Constant(1/5))
    f = One()
    col = Collection(a, b, c, d, e, f)
    
    assert col._disassembled_quantities == [a, b, c, d, *e.factors, f]


def test_base_quantities():
    a = Quantity('a', A=2, B=3, C=5, scaling=True)
    b = Constant('b')
    c = Power(a, -2, dependent=True)
    d = Constant(1/5)
    e = Product(a, b, c, Constant(1/5))
    f = One()
    col = Collection(a, b, c, d, e, f)
    
    assert col._base_quantities == [a, b]

def test_show(capfd):
    a = Quantity('a', A=2, scaling=True)
    b = Constant('b')
    c = Power(a, -2, dependent=True)
    d = Product(a, b, c, Constant(1/5))
    e = One()
    col = Collection(a, b, c, d, e)

    col.show()
    out, _ = capfd.readouterr()
    assert out == ('\n'
                   '          ⎛      1   1/5⋅𝐛   ⎞\n'
                   'Collection⎜a, 𝐛, ──, ─────, 1⎟\n'
                   '          ⎜       2    a     ⎟\n'
                   '          ⎝      a           ⎠\n'
                   '\n')


def test_wrong_type():
    with raises(TypeError):
        Collection(Quantity('a'), 123, 'oi', (1,2,3))


def test_repeated_quantity_names():
    a = Quantity('a', A=3)
    b = Quantity('a', B=2, dependent=True)
    c = Quantity('a', A=3, scaling=True)
    
    with raises(ValueError):
        Collection(a, b, c)


def test_equal_dimensions():
    a = Quantity('a', A=2, B=3, C=5, scaling=True)
    b = Quantity('b', A=2, B=3, C=5, dependent=True)
    c = Quantity('c', A=4, B=6, C=10)
    col = Collection(a, b, c**(1/2))

    assert col._dimensions == a.dimension._dimensions


def test_set_dimensions():
    a = Quantity('a', A=1, B=0, C=9, scaling=True)
    b = Quantity('b', A=-1, B=10, C=7, dependent=True)
    c = Quantity('c', A=2, B=5, C=-6)
    col = Collection(a,b,c)
    col._set_dimensions(A=1, B=2)

    assert col._dimensions == dict(A=1, B=2, C=0)

    with raises(ValueError):
        col._set_dimensions(D=55)


def test_clear_null_dimensions():
    a = Quantity('a', A=1, B=0, C=9, scaling=True)
    b = Quantity('b', A=-1, B=10, C=7, dependent=True)
    c = Quantity('c', A=2, B=5, C=-6)
    col = Collection(a,b,c)
    col._set_dimensions(A=1, B=2)
    col._clear_null_dimensions()

    assert col._dimensions == dict(A=1, B=2)


def test_constants():
    a = Quantity('a', A=1, B=0, C=9, scaling=True)
    b = Quantity('b', A=-1, B=10, C=7, dependent=True)
    c = Constant('c')
    d = One()
    e = Constant('sqrt(2)')
    col = Collection(d, a, b, c, e)
    col._set_constants()

    assert col._constants == [d, c, e]

    col._clear_constants(only_ones=True)

    assert col._constants == [c, e]

    col._clear_constants(only_numbers=True)

    assert col._constants == [c]

    col = Collection(d, a, b, c, e)
    col._clear_constants()

    assert col._constants == []


def test_scaling_quantities():
    a = Quantity('a', A=1, B=0, C=9, scaling=True)
    b = Quantity('b', A=-1, B=10, C=7, dependent=True)
    c = Product(a, b, scaling=True)
    d = Power(b, -4, scaling=True)
    e = Power(a, 5)
    col = Collection(a,b,c,d,e)
    col._set_scaling_quantities()

    assert col._scaling_quantities == [a, c, d]
    assert col._nonscaling_quantities == [b, e]


def test_dependent_quantities():
    a = Quantity('a', A=1, B=0, C=9, scaling=True)
    b = Quantity('b', A=-1, B=10, C=7, dependent=True)
    c = Product(a, b, scaling=True)
    d = Power(b, -4, dependent=True)
    e = Power(a, 5, dependent=True)
    col = Collection(a,b,c,d,e)
    col._set_dependent_quantities()

    assert col._dependent_quantities == [b, d, e]
    assert col._independent_quantities == [a, c]


def test_matrix():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=1)
    e = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    col1 = Collection(a,b,c,e)
    col1._set_matrix_independent_rows()

    assert col1._matrix == ImmutableDenseMatrix([[-1,  1, 2,  0],
                                                 [10,  0, 3,  4],
                                                 [ 7,  9, 3, -3],
                                                 [16, 10, 8,  2]])
    assert col1._rank == 4
    assert col1._rcef == ImmutableDenseMatrix([[1, 0, 0, 0],
                                               [0, 1, 0, 0],
                                               [0, 0, 1, 0],
                                               [0, 0, 0, 1]])
    assert col1._independent_rows == (0, 1, 2, 3)
    assert col1._independent_dimensions == dict(A=S.NaN, B=S.NaN, C=S.NaN, D=S.NaN)

    col2 = Collection(a,b,c,d)
    with catch_warnings(record=True) as w:
        col2._set_matrix_independent_rows()
        assert len(w) == 1
        assert issubclass(w[-1].category, NodimoWarning)

    assert col2._rank == 3
    assert col2._rcef == ImmutableDenseMatrix([[1, 0, 0, 0],
                                               [0, 1, 0, 0],
                                               [0, 0, 1, 0],
                                               [1, 1, 1, 0]])
    assert col2._independent_rows == (0, 1, 2)
    assert col2._independent_dimensions == dict(A=S.NaN, B=S.NaN, C=S.NaN)


def test_submatrices():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    col1 = Collection()
    col1._set_submatrices()
    col2 = Collection(a,b,c,d)
    col2._set_submatrices()

    assert col1._submatrices == {}
    assert col2._submatrices[a] == ImmutableDenseMatrix([-1, 10, 7, 16])
    assert col2._submatrices[b] == ImmutableDenseMatrix([1, 0, 9, 10])
    assert col2._submatrices[c] == ImmutableDenseMatrix([2, 3, 3, 8])
    assert col2._submatrices[d] == ImmutableDenseMatrix([0, 4, -3, 2])


def test_submatrix():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    col = Collection(a,b,c,d)

    assert col._get_submatrix(a,b) == ImmutableDenseMatrix([[-1,  1],
                                                            [10,  0],
                                                            [ 7,  9],
                                                            [16, 10]])
    assert col._get_submatrix(a,c,d) == ImmutableDenseMatrix([[-1,  2,  0],
                                                              [10,  3,  4],
                                                              [ 7,  3, -3],
                                                              [16, 8,  2]])
    with raises(ValueError):
        col._get_submatrix(a,b,15)


def test_hash():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)
    dicio = {col:col}

    assert dicio[col] == col


def test_equality():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    e = Constant('2*pi')
    col1 = Collection(a,b,c,d)
    col2 = Collection(d,a,c,b)
    col3 = Collection(a,b,c,d,a)
    col4 = Collection(a,b,c,d,e)
    
    assert col1 == col1
    assert col1 == col2
    assert col1 == col3
    assert not col1 == col4
    assert col1 != [a,b,c,d]


def test_contains_and_length():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)

    assert a in col
    assert c in col
    assert e in col
    assert len(col) == 5


def test_iteration():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)
    col_iter = iter(col)

    assert next(col_iter) == a
    assert next(col_iter) == b
    assert next(col_iter) == c
    assert next(col_iter) == d
    assert next(col_iter) == e
    assert col.__next__() == a


def test_getitem():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Quantity('c', A=2, B=3, C=3, D=8)
    d = Quantity('d', A=0, B=4, C=-3, D=2, scaling=True)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)

    assert col[0] == a
    assert col[0:2] == [a,b]
    assert col[-1] == e


def test_sympification():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Power(a,-2)
    d = Product(a,b,c, reduce=False)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)

    assert sympify(col) == sympify(list(sympify(qty) for qty in col))


def test_repr_latex_():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Power(a,-2)
    d = Product(a,b,c, reduce=False)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)

    assert col._repr_latex_() == '$\\displaystyle \\mathtt{\\text{Collection}}\\left(a,\\ b,\\ \\frac{1}{{a}^{2}},\\ \\frac{a b}{{a}^{2}},\\ 2 \\pi\\right)$'


def test_sympyrepr():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Power(a,-2)
    d = Product(a,b,c, reduce=False)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)

    assert srepr(col) == ("Collection(Quantity('a', A=-1, B=10, C=7, D=16, scaling=True), "
                          "Quantity('b', A=1, C=9, D=10, dependent=True), "
                          "Power(Quantity('a', A=-1, B=10, C=7, D=16, scaling=True), -2), "
                          "Product(Quantity('a', A=-1, B=10, C=7, D=16, scaling=True), "
                            "Quantity('b', A=1, C=9, D=10, dependent=True), "
                            "Power(Quantity('a', A=-1, B=10, C=7, D=16, scaling=True), -2), reduce=False), "
                          "Constant('2*pi'))")


def test_sympystr():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Power(a,-2)
    d = Product(a,b,c, reduce=False)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)

    assert str(col) == 'Collection(a, b, 1/a**2, a*b/a**2, 2*pi)'


def test_latex():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Power(a,-2)
    d = Product(a,b,c, reduce=False)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)

    assert latex(col) == '\\mathtt{\\text{Collection}}\\left(a,\\ b,\\ \\frac{1}{{a}^{2}},\\ \\frac{a b}{{a}^{2}},\\ 2 \\pi\\right)'


def test_pretty():
    a = Quantity('a', A=-1, B=10, C=7, D=16, scaling=True)
    b = Quantity('b', A=1, B=0, C=9, D=10, dependent=True)
    c = Power(a,-2)
    d = Product(a,b,c, reduce=False)
    e = Constant('2*pi')
    col = Collection(a,b,c,d,e)
    pretty_col = pretty(col)

    # sympy < 1.13
    pretty1 = ('          ⎛      1   a⋅b     ⎞\n'
               'Collection⎜a, b, ──, ───, 2⋅π⎟\n'
               '          ⎜       2    2     ⎟\n'
               '          ⎝      a    a      ⎠')

    # sympy >= 1.13
    pretty2 = ('          ⎛      1   a⋅b     ⎞\n'
               'Collection⎜a, b, ──, ───, 2⋅π⎟\n'
               '          ⎜       2   2      ⎟\n'
               '          ⎝      a   a       ⎠')

    assert pretty_col == pretty1 or pretty_col == pretty2
