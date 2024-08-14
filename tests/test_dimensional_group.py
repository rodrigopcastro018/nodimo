from sympy import srepr, Number, ImmutableDenseMatrix
from pytest import raises
from nodimo.quantity import Quantity
from nodimo.groups import DimensionalGroup


def test_quantities():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', C=3, dependent=True)
    c = Quantity('c', A=1, scaling=True)
    d = Quantity('d')
    grp1 = DimensionalGroup(a, b, c, d)
    grp2 = DimensionalGroup(a, b, c, d, A=1, C=1)

    assert grp1._original_quantities == [a, b, c, d]
    assert grp2._original_quantities == [a, b, c, d]
    assert grp1.quantities == [b*a**(3/4)/c**(9/4), d]
    assert grp2.quantities == [b*a**(1/2)/c**(1/2), d*c**(7/4)/a**(1/4), c**(7/4)/a**(1/4)]


def test_dimensions():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', C=3, dependent=True)
    c = Quantity('c', A=1, scaling=True)
    d = Quantity('d')
    grp1 = DimensionalGroup(a, b, c, d)
    grp2 = DimensionalGroup(a, b, c, d, A=1, C=1)

    assert grp1._dimensions == {}
    assert grp2._dimensions == {'A':1, 'C':1}


def test_scaling_properties():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', C=3, dependent=True)
    c = Quantity('c', A=1, scaling=True)
    d = Quantity('d')
    grp = DimensionalGroup(a, b, c, d, A=1, C=1)

    assert grp._scaling_quantities == [a, c]
    assert grp._nonscaling_quantities == [b, d]
    assert grp._scaling_matrix == ImmutableDenseMatrix([[ 3, 1],
                                                        [-4, 0]])
    assert grp._nonscaling_matrix == ImmutableDenseMatrix([[0, 0],
                                                           [3, 0]])


def test_group_validation():
    with raises(ValueError):
        a = Quantity('a', A=3, B=2, C=-4)
        b = Quantity('b', A=0, B=0, C=3, dependent=True)
        c = Quantity('c', A=1, B=0, C=0, scaling=True)
        d = Quantity('d')
        e = Quantity('e', A=0, B=6, C=0, scaling=True)
        DimensionalGroup(a, b, c, d, e)

    with raises(ValueError):
        a = Quantity('a', A=3, B=2, C=-4, scaling=True)
        b = Quantity('b', C=3, dependent=True)
        c = Quantity('c', A=6, B=4, C=-8, scaling=True)
        d = Quantity('d')
        e = Quantity('e', B=6, scaling=True)
        DimensionalGroup(a, b, c, d, e)


def test_exponents():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', C=3, dependent=True)
    c = Quantity('c', A=1, scaling=True)
    d = Quantity('d')
    grp = DimensionalGroup(a, b, c, d, A=1, C=1)

    assert grp._exponents == ImmutableDenseMatrix([[           1,            0,            0],
                                                   [           0,            1,            0],
                                                   [ Number(1,2), Number(-1,4), Number(-1,4)],
                                                   [Number(-1,2),  Number(7,4),  Number(7,4)]])


def test_sympyrepr():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', C=3, dependent=True)
    c = Quantity('c', A=1, scaling=True)
    d = Quantity('d')
    grp1 = DimensionalGroup(a, b, c, d)
    grp2 = DimensionalGroup(a, b, c, d, A=1, C='pi')

    assert srepr(grp1) == "DimensionalGroup(Quantity('a', A=3, C=-4, scaling=True), Quantity('b', C=3, dependent=True), Quantity('c', A=1, scaling=True), Quantity('d'))"
    assert srepr(grp2) == "DimensionalGroup(Quantity('a', A=3, C=-4, scaling=True), Quantity('b', C=3, dependent=True), Quantity('c', A=1, scaling=True), Quantity('d'), A=1, C='pi')"
