from warnings import catch_warnings
from nodimo.quantity import Quantity, Constant
from nodimo.product import Product
from nodimo.groups import Group, HomogeneousGroup
from nodimo._internal import NodimoWarning


def test_group():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', B=3, dependent=True)
    c = Constant(9/7)
    d = Product(Quantity('e'), a)
    e = Quantity('a', A=3, C=-4, dependent=True)
    grp1 = Group(a, b, c, d)

    assert grp1.quantities == [a, b, c, d]

    with catch_warnings(record=True) as w:
        grp2 = Group(a, b, c, d, e)
        assert len(w) == 1
        assert issubclass(w[-1].category, NodimoWarning)
    
    assert grp2.quantities == [a, b, c, d]


def test_homogeneous_group():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', B=3, dependent=True)
    c = Constant(9/7)
    d = Product(Quantity('e'), a)
    f = Quantity('f', A=3, C=-4, dependent=True)
    grp1 = HomogeneousGroup(a, c, d, f)

    assert grp1.quantities == [a, c, d, f]

    with catch_warnings(record=True) as w:
        grp2 = HomogeneousGroup(a, b, c, d, f)
        assert len(w) == 1
        assert issubclass(w[-1].category, NodimoWarning)

    assert grp2.quantities == [a, c, d, f]
