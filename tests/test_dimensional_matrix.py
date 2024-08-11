from sympy import srepr, latex, pretty, sympify, Symbol, ImmutableDenseMatrix
from nodimo.quantity import Quantity
from nodimo.matrix import DimensionalMatrix


def test_properties():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    dm = DimensionalMatrix(a, b, c)

    assert dm.matrix == ImmutableDenseMatrix([[ 3,  1, -5],
                                              [-1,  0,  0],
                                              [ 0, -4,  0]])
    assert dm.rank == 3
    assert dm.independent_rows == (0,1,2)


def test_dimensions():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    dm = DimensionalMatrix(a, b, c)

    assert tuple(dm._dimensions.keys()) == ('A', 'B', 'C')

    dm.set_dimensions_order('B', 'C', 'A')

    assert tuple(dm._dimensions.keys()) == ('B', 'C', 'A')

    dm.set_dimensions_order('C')

    assert tuple(dm._dimensions.keys()) == ('C', 'B', 'A')


def test_symbolic():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    dm = DimensionalMatrix(a, b, c)
    ax = a._symbolic
    bx = b._symbolic
    cx = c._symbolic
    A = Symbol('A')
    B = Symbol('B')
    C = Symbol('C')
    N = Symbol('')

    assert dm._symbolic == ImmutableDenseMatrix([[N, ax, bx, cx],
                                                 [A,  3,  1, -5],
                                                 [B, -1,  0,  0],
                                                 [C,  0, -4,  0]])


def test_sympify():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    dm = DimensionalMatrix(a, b, c)

    assert sympify(dm) == ImmutableDenseMatrix([[ 3,  1, -5],
                                                [-1,  0,  0],
                                                [ 0, -4,  0]])


def test_sympyrepr():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    d = b*c*a**-2
    e = c**-5
    dm = DimensionalMatrix(a, d, e)

    assert srepr(dm) == "DimensionalMatrix(Quantity('a', A=3, B=-1), Product(Quantity('b', C=-4, A=1, scaling=True), Quantity('c', A=-5), Power(Quantity('a', A=3, B=-1), -2)), Power(Quantity('c', A=-5), -5))"


def test_sympystr():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    d = b*c*a**-2
    e = c**-5
    dm = DimensionalMatrix(a, d, e)

    assert str(dm) == '    a  b*c/a**2  1/c**5\nA   3       -10      25\nB  -1         2       0\nC   0        -4       0'


def test_latex():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    d = b*c*a**-2
    e = c**-5
    dm = DimensionalMatrix(a, d, e)

    assert latex(dm) == '\\begin{array}{r|rrr} & a & \\frac{b c}{{a}^{2}} & \\frac{1}{{c}^{5}} \\\\ \\hline \\mathsf{A} & \\phantom{-}3 & -10 & \\phantom{-}25 \\\\ \\mathsf{B} & -1 & \\phantom{-}2 & \\phantom{-}0 \\\\ \\mathsf{C} & \\phantom{-}0 & -4 & \\phantom{-}0 \\\\ \\end{array}'


def test_pretty():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5)
    d = b*c*a**-2
    e = c**-5
    dm = DimensionalMatrix(a, d, e)

    assert pretty(dm) == ('       b⋅c  1 \n'
                          '    a  ───  ──\n'
                          '        2    5\n'
                          '       a    c \n'
                          'A   3  -10  25\n'
                          'B  -1    2   0\n'
                          'C   0   -4   0')
