from warnings import catch_warnings
from nodimo.quantity import Quantity, Constant
from nodimo.product import Product
from nodimo.power import Power
from nodimo.groups import IndependentGroup
from nodimo._internal import NodimoWarning


def test_quantities():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', B=3, dependent=True)
    c = Constant(9/7)
    d = Product(a, b, c)
    e = Quantity('e')
    f = Power(e, -2, dependent=True)
    g = Product(b, f, scaling=True)
    grp1 = IndependentGroup(a, b, e)

    assert grp1.quantities == [a, b, e]

    with catch_warnings(record=True) as w:
        grp2 = IndependentGroup(a, b, c, d, e, f, g)
        assert len(w) == 1
        assert issubclass(w[-1].category, NodimoWarning)
    
    assert grp2.quantities == [a, b, e]


def test_derived_quantities():
    a = Quantity('a', A=3, C=-4, scaling=True)
    b = Quantity('b', B=3, dependent=True)
    c = Constant(9/7)
    d = Product(a, b, c)
    e = Quantity('e')
    f = Power(e, -2, dependent=True)
    g = Product(b, f, scaling=True)
    grp = IndependentGroup(a, d, g)

    dq0 = Quantity('dQ0', a=1)
    dq1 = Quantity('dQ1', a=1, b=1)
    dq2 = Quantity('dQ2', b=1, e=-2)

    assert list(grp._derived_quantities) == [dq0, dq1, dq2]
