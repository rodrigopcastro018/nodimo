from sympy import srepr, latex, pretty
from pytest import raises
from nodimo.quantity import Quantity, Constant
from nodimo.product import Product
from nodimo.groups import ScalingGroup


def test_id_number():
    a = Quantity('a', A=3, scaling=True)
    b = Quantity('b', B=-4)
    c = Quantity('c', B=1, C=5)
    grp1 = ScalingGroup(a, b, c)
    grp2 = ScalingGroup(a, b, c, id_number=10)

    assert grp1._id_number == 0
    assert grp2._id_number == 10


def test_quantities():
    a = Quantity('a', A=3, scaling=True)
    b = Quantity('b', B=-4)
    c = Quantity('c', B=1, C=5)
    d = Constant('D')
    grp = ScalingGroup(a, b, c, d)

    assert grp.quantities == [a, b, c]
    assert grp.quantities[0].is_scaling
    assert grp.quantities[1].is_scaling
    assert grp.quantities[2].is_scaling


def test_rank():
    a = Quantity('a', A=3, scaling=True)
    b = Quantity('b', B=-4)
    c = Quantity('c', B=1, C=5)
    d = Quantity('d', A=-1, B=-2, C=-10, scaling=True)
    grp = ScalingGroup(a, b, c)

    assert grp._rank == 3

    with raises(ValueError):
        ScalingGroup(a, b, c, d)


def test_sympyrepr():
    a = Quantity('a', A=3, scaling=True)
    b = Quantity('b', B=-4)
    c = Quantity('c', B=1, C=5)
    grp1 = ScalingGroup(a, b, c)
    grp2 = ScalingGroup(a, b, c, id_number=8)

    assert srepr(grp1) == "ScalingGroup(Quantity('a', A=3, scaling=True), Quantity('b', B=-4), Quantity('c', B=1, C=5))"
    assert srepr(grp2) == "ScalingGroup(Quantity('a', A=3, scaling=True), Quantity('b', B=-4), Quantity('c', B=1, C=5), id_number=8)"


def test_sympystr():
    a = Quantity('a', A=3, scaling=True)
    b = Quantity('b', B=-4)
    c = Quantity('c', B=1, C=5)
    grp1 = ScalingGroup(a, b, c)
    grp2 = ScalingGroup(a, b, c, id_number=8)

    assert str(grp1) == 'Scaling group (a, b, c)'
    assert str(grp2) == 'Scaling group 8 (a, b, c)'


def test_latex():
    a = Quantity('a', A=3, scaling=True)
    b = Quantity('b', B=-4)
    c = Quantity('c', B=1, C=5)
    grp1 = ScalingGroup(a, b, c)
    grp2 = ScalingGroup(a, b, c, id_number=8)

    assert latex(grp1) == '\\mathtt{\\text{Scaling group }}\\left(a,\\ b,\\ c\\right)'
    assert latex(grp2) == '\\mathtt{\\text{Scaling group 8 }}\\left(a,\\ b,\\ c\\right)'


def test_pretty():
    a = Quantity('a', A=3, scaling=True)
    b = Quantity('b', B=-4)
    c = Quantity('c', B=1, C=5)
    d = Product(a, c**-1, scaling=True)
    grp1 = ScalingGroup(a, b, d)
    grp2 = ScalingGroup(a, b, d, id_number=8)

    assert pretty(grp1) == '              ⎛      a⎞\nScaling group ⎜a, b, ─⎟\n              ⎝      c⎠'
    assert pretty(grp2) == '                ⎛      a⎞\nScaling group 8 ⎜a, b, ─⎟\n                ⎝      c⎠'
