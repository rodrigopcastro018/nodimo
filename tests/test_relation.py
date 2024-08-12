from sympy import srepr, latex, pretty, sympify, Function, Equality
from pytest import raises
from nodimo.quantity import Quantity, Constant
from nodimo.product import Product
from nodimo.power import Power
from nodimo.relation import Relation


def test_name():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1)
    d = Product(b, c, a**-2, dependent=True)
    e = Power(Quantity('h', C=-1), -5)
    rel1 = Relation(c, d, e)
    rel2 = Relation(c, d, e, name='Phi')

    assert rel1._name == 'f'
    assert rel2._name == 'Phi'


def test_validation():
    a = Quantity('a', A=3, B=-1, dependent=True)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1, dependent=True)
    d = Product(b, c, a**-2, dependent=True)
    e = Power(Quantity('h', C=-1), -5)

    with raises(ValueError):
        Relation(c, d, e)


def test_no_dependent_quantity():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1)
    d = Product(b, c, a**-2)
    e = Power(Quantity('h', C=-1), -5)
    rel = Relation(c, d, e)

    assert rel._dependent_quantities == (Constant('const'),)


def test_symbolic_and_sympify():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1, dependent=True)
    rel = Relation(a, b, c)

    func = Function('f')(a, b)
    relation = Equality(c, func)

    assert rel._symbolic == relation
    assert sympify(rel) == relation


def test_equality():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1)
    d = Product(b, c, a**-2, dependent=True)
    e = Power(Quantity('h', C=-1), -5)
    rel1 = Relation(c, d, e)
    rel2 = Relation(c, d, e, name='Phi')

    assert rel1 == rel2


def test_sympyrepr():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1)
    d = Product(b, c, a**-2)
    e = Power(Quantity('h', C=-1), -5)
    rel = Relation(c, d, e)

    assert srepr(rel) == "Relation(Quantity('c', A=-5, B=2, C=1), Product(Quantity('b', C=-4, A=1, scaling=True), Quantity('c', A=-5, B=2, C=1), Power(Quantity('a', A=3, B=-1), -2)), Power(Quantity('h', C=-1), -5))"


def test_sympystr():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1)
    d = Product(b, c, a**-2)
    e = Power(Quantity('h', C=-1), -5)
    rel = Relation(c, d, e)

    assert str(rel) == '𝐜𝐨𝐧𝐬𝐭 = f(c, b*c/a**2, 1/h**5)'


def test_latex():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1)
    d = Product(b, c, a**-2)
    e = Power(Quantity('h', C=-1), -5)
    rel = Relation(c, d, e)

    assert latex(rel) == '𝐜𝐨𝐧𝐬𝐭 = f\\left(c,\\ \\frac{b c}{{a}^{2}},\\ \\frac{1}{{h}^{5}}\\right)'


def test_pretty():
    a = Quantity('a', A=3, B=-1)
    b = Quantity('b', C=-4, A=1, scaling=True)
    c = Quantity('c', A=-5, B=2, C=1)
    d = Product(b, c, a**-2)
    e = Power(Quantity('h', C=-1), -5)
    rel = Relation(c, d, e)
    pretty_rel = pretty(rel)

    # sympy < 1.13
    pretty1 = ('         ⎛   b⋅c  1 ⎞\n'
               '𝐜𝐨𝐧𝐬𝐭 = f⎜c, ───, ──⎟\n'
               '         ⎜     2   5⎟\n'
               '         ⎝    a   h ⎠')

    # sympy >= 1.13
    pretty2 = ('         ⎛   b⋅c  1 ⎞\n'
               '𝐜𝐨𝐧𝐬𝐭 = f⎜c, ───, ──⎟\n'
               '         ⎜    2    5⎟\n'
               '         ⎝   a    h ⎠')

    assert pretty_rel == pretty1 or pretty_rel == pretty2
