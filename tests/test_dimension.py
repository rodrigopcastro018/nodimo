from sympy import srepr, latex, pretty, Symbol, Number, S
from pytest import raises
from nodimo.dimension import Dimension


def test_dimensions():
    dim1 = Dimension(a=1/2, b=-5, c=10)
    dim2 = Dimension(a=000, b=-1.111, c=0, d=0.0)
    dim3 = Dimension()

    assert dim1._dimensions == dict(a=Number(1,2), b=Number(-5), c=Number(10))
    assert dim2._dimensions == dict(b=Number(-1.111))
    assert dim3._dimensions == dict()


def test_dimensionless():
    dim1 = Dimension()
    dim2 = Dimension(a=0, b=0, c=0)
    dim3 = Dimension(a=1.5)

    assert dim1._is_dimensionless
    assert dim2._is_dimensionless
    assert not dim3._is_dimensionless


def test_symbolic():
    dim1 = Dimension(a=1/2, b=-5, c=10)
    dim2 = Dimension()
    sym1 = (Symbol('a', commutative=False)**Number(1,2)
           * Symbol('b', commutative=False)**Number(-5)
           * Symbol('c', commutative=False)**Number(10))
    sym2 = S.One

    assert dim1._symbolic == sym1
    assert dim2._symbolic == sym2


def test_copy():
    dim = Dimension(A=1, B=2, C=-3, D=1/2, E=4/5, F=-5/6,
                    G='sqrt(7)', H='2*sqrt(2)',I='sqrt(2)/2', J='pi')
    
    assert dim == dim._copy()


def test_multiplication():
    dim1 = Dimension(A=1, B=2, C=1/3, D=0)
    dim2 = Dimension(A=2, B=-1, C=2/3, D=-2)
    dim3 = dim1 * dim2

    assert dim3 == Dimension(A=3, B=1, C=1, D=-2)

    with raises(NotImplementedError):
        dim1.__mul__(dict(A=1, B=2, C=3, D=4))


def test_exponentiation():
    dim = Dimension(A=4, B=3, C=-2/3, D=-2)
    exp = 3

    assert dim**exp == Dimension(A=12, B=9, C=-2, D=-6)


def test_division():
    dim1 = Dimension(A=1, B=2, C=1/3, D=0)
    dim2 = Dimension(A=2, B=-1, C=2/3, D=-2)
    dim3 = dim1 / dim2

    assert dim3 == Dimension(A=-1, B=3, C=-1/3, D=2)

    with raises(NotImplementedError):
        dim1.__truediv__(dict(A=1, B=2, C=3, D=4))


def test_repr_latex():
    dim = Dimension(A=2, B=-1, C=2/3)

    assert dim._repr_latex_() == (
        '$\\displaystyle \\mathsf{A}^{2} \\mathsf{B}^{-1} \\mathsf{C}^{\\frac{2}{3}}$'
    )


def test_sympyrepr():
    dim = Dimension(A=1, B=2, C=-3, D=1/2, E=4/5, F=-5/6,
                    G='sqrt(7)', H='2*sqrt(2)',I='sqrt(2)/2', J='pi')

    assert srepr(dim) == ("Dimension(A=1, B=2, C=-3, D=(1, 2), E=(4, 5), F=(-5, 6), "
                          "G='sqrt(7)', H='2*sqrt(2)', I='sqrt(2)/2', J='pi')")


def test_sympystr():
    dim1 = Dimension()
    dim2 = Dimension(A=1, B=2, C=-3, D=1/2, E=4/5, F=-5/6,
                    G='sqrt(7)', H='2*sqrt(2)',I='sqrt(2)/2', J='pi')

    assert str(dim1) == '1'
    assert str(dim2) == (
        'A'
        '*B**2'
        '*C**(-3)'
        '*D**(1/2)'
        '*E**(4/5)'
        '*F**(-5/6)'
        '*G**sqrt(7)'
        '*H**(2*sqrt(2))'
        '*I**(sqrt(2)/2)'
        '*J**pi'
    )


def test_latex():
    dim1 = Dimension()
    dim2 = Dimension(A=1, B=2, C=-3, D=1/2, E=4/5, F=-5/6,
                    G='sqrt(7)', H='2*sqrt(2)',I='sqrt(2)/2', J='pi')

    assert latex(dim1) == '\\mathsf{1}'
    assert latex(dim2) == (
        '\\mathsf{A} '
        '\\mathsf{B}^{2} '
        '\\mathsf{C}^{-3} '
        '\\mathsf{D}^{\\frac{1}{2}} '
        '\\mathsf{E}^{\\frac{4}{5}} '
        '\\mathsf{F}^{- \\frac{5}{6}} '
        '\\mathsf{G}^{\\sqrt{7}} '
        '\\mathsf{H}^{2 \\sqrt{2}} '
        '\\mathsf{I}^{\\frac{\\sqrt{2}}{2}} '
        '\\mathsf{J}^{\\pi}'
    )


def test_pretty():
    dim1 = Dimension()
    dim2 = Dimension(A=1, B=2, C=-3, D=1/2, E=4/5, F=-5/6,
                    G='sqrt(7)', H='2*sqrt(2)',I='sqrt(2)/2', J='pi')

    assert pretty(dim1) == '1'
    assert pretty(dim2) == (
        '                                    √2   \n'
        '                                    ──   \n'
        '   2  -3  1/2  4/5  -5/6  √7  2⋅√2  2   π\n'
        'A⋅B ⋅C  ⋅D   ⋅E   ⋅F    ⋅G  ⋅H    ⋅I  ⋅J '
    )
    assert pretty(dim2, use_unicode=False) == (
        '                                            ___    \n'
        '                                          \\/ 2     \n'
        '                            ___      ___  -----    \n'
        '   2  -3  1/2  4/5  -5/6  \\/ 7   2*\\/ 2     2    pi\n'
        'A*B *C  *D   *E   *F    *G     *H       *I     *J  '
    )
