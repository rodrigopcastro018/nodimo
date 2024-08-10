from sympy import srepr, latex, pretty, Symbol, sympify
from pytest import raises
from nodimo.dimension import Dimension
from nodimo.quantity import Quantity
from nodimo.product import Product
from nodimo.power import Power


def test_name():
    qty = Quantity('qty')
    assert qty.name == 'qty'

    with raises(TypeError):
        Quantity(123)
    
    with raises(ValueError):
        Quantity(' ')


def test_dimension():
    qty1 = Quantity('qty1')
    qty2 = Quantity('qty2', A=0, B=-2, C=3/2)

    assert qty1.dimension == Dimension()
    assert qty2.dimension == Dimension(B=-2, C=3/2)
    assert qty1.is_dimensionless
    assert not qty2.is_dimensionless


def test_dependent():
    qty1 = Quantity('qty1', A=1, B=2, C=3, dependent=True)
    qty2 = Quantity('qty2', A=4, B=5, C=6, dependent=False)
    qty3 = Quantity('qty3', A=7, B=8, C=9)

    assert qty1.is_dependent
    assert not qty2.is_dependent
    assert not qty3.is_dependent


def test_scaling():
    qty1 = Quantity('qty1', A=1, B=2, C=3, scaling=True)
    qty2 = Quantity('qty2', A=4, B=5, C=6, scaling=False)
    qty3 = Quantity('qty3', A=7, B=8, C=9)

    assert qty1.is_scaling
    assert not qty2.is_scaling
    assert not qty3.is_scaling


def test_dependent_and_scaling():
    with raises(ValueError):
        Quantity('qty', A=1, dependent=True, scaling=True)

    with raises(ValueError):
        qty1 = Quantity('qty1', A=1)
        qty1._is_dependent = True
        qty1._is_scaling = True
        qty1._validate_quantity()

    with raises(ValueError):
        qty2 = Quantity('qty2', A=1)
        qty2._is_scaling = True
        qty2._is_dependent = True
        qty2._validate_quantity()


def test_scaling_and_dimensionless():
    with raises(ValueError):
        Quantity('qty', scaling=True)

    qty = Quantity('qty')
    with raises(ValueError):
        qty._is_scaling = True
        qty._validate_quantity()


def test_symbolic():
    qty1 = Quantity('a0')
    qty2 = Quantity('alpha')

    assert qty1._symbolic == Symbol('a0')
    assert qty2._symbolic == Symbol('alpha')


def test_fixed_attributes():
    qty = Quantity('qty')

    assert not qty._is_power
    assert not qty._is_product
    assert not qty._is_derived
    assert not qty._is_one
    assert not qty._is_constant
    assert not qty._is_number
    assert not qty._is_quotient
    assert qty._is_reduced
    assert qty._unreduced is qty


def test_copy():
    qty = Quantity('qty', A=1, B=-2, C=5)
    assert qty._copy() == qty


def test_reduce():
    qty = Quantity('qty', A=1, B=-2, C=5)
    assert qty.reduce() is qty


def test_equality():
    qty1 = Quantity('qty', A=1, B=-2, C=3/2)
    qty2 = Quantity('qty', B=-2, C=3/2, A=1)
    qty3 = Quantity('qty', C=3/2, A=1, B=-2, scaling=True)
    qty4 = Quantity('qty', A=1, C=3/2, B=-2, dependent=True)
    qty5 = Quantity('qtyy', A=1, B=-2, C=3/2)
    qty6 = Quantity('qty', A=1, B=-2, C=-3/2)

    assert qty1 == qty1
    assert qty1 == qty2
    assert qty2 == qty3
    assert qty3 == qty4
    assert qty1 != qty5
    assert qty1 != qty6


def test_multiplication():
    qty1 = Quantity('qty1', A=1, B=-2, C=3/2)
    qty2 = Quantity('qty2', A=2, B=1, C=-1/2)
    prod = Product(qty1, qty2)

    assert prod == qty1 * qty2

    with raises(NotImplementedError):
        qty1.__mul__(Symbol('sym1'))


def test_exponentiation():
    qty = Quantity('qty', A=1, B=-2, C=3/2)
    pow = Power(qty, -3)

    assert pow == qty**-3


def test_division():
    qty1 = Quantity('qty1', A=1, B=-2, C=3/2)
    qty2 = Quantity('qty2', A=2, B=1, C=-1/2)
    div = Product(qty1, Power(qty2,-1))

    assert div == qty1/qty2

    with raises(NotImplementedError):
        qty1.__truediv__(Symbol('sym1'))


def test_sympify():
    qty = Quantity('qty', A=1, B=-2, C=3/2)
    assert sympify(qty) == Symbol('qty')


def test_repr_latex():
    qty = Quantity('qty', A=1, B=-2, C=3/2)
    assert qty._repr_latex_() == '$\\displaystyle qty$'


def test_sympyrepr():
    qty1 = Quantity('qty1', A=1, B=-2, C=3/2)
    qty2 = Quantity('qty2', C=3/2, A=1, B=-2, scaling=True)
    qty3 = Quantity('qty3', A=1, C=3/2, B=-2, dependent=True)

    assert srepr(qty1) == "Quantity('qty1', A=1, B=-2, C=(3, 2))"
    assert srepr(qty2) == "Quantity('qty2', C=(3, 2), A=1, B=-2, scaling=True)"
    assert srepr(qty3) == "Quantity('qty3', A=1, C=(3, 2), B=-2, dependent=True)"


def test_sympystr():
    qty1 = Quantity('a')
    qty2 = Quantity('a0')
    qty3 = Quantity('alpha')

    assert str(qty1) == 'a'
    assert str(qty2) == 'a0'
    assert str(qty3) == 'alpha'


def test_latex():
    qty1 = Quantity('a')
    qty2 = Quantity('a0')
    qty3 = Quantity('alpha')

    assert latex(qty1) == 'a'
    assert latex(qty2) == 'a_{0}'
    assert latex(qty3) == '\\alpha'


def test_pretty():
    qty1 = Quantity('a')
    qty2 = Quantity('a0')
    qty3 = Quantity('alpha')

    assert pretty(qty1) == 'a'
    assert pretty(qty2) == 'a₀'
    assert pretty(qty3) == 'α'
