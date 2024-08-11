from sympy import srepr, latex, pretty, Symbol, Number, S, sympify
from pytest import raises
from nodimo.quantity import Constant, One
from nodimo.product import Product
from nodimo.power import Power
from nodimo._internal import _prettify_name


def test_converted_value():
    cval1 = Constant._convert_value('a')
    cval2 = Constant._convert_value('1/2')
    cval3 = Constant._convert_value('1')

    assert cval1 == 'a'
    assert cval2 == Number(1,2)
    assert cval3 == S.One

    with raises(TypeError):
        Constant(('x',))


def test_name():
    const1 = Constant('A')
    const2 = Constant(1/2)
    const3 = Constant(1)

    assert const1.name == _prettify_name('A', bold=True)
    assert const2.name == '1/2'
    assert const3.name == '1'
    assert const1._constant_name == 'A'
    assert const2._constant_name == '1/2'
    assert const3._constant_name == '1'


def test_dimension():
    const1 = Constant('A')
    const2 = Constant(1/2)

    assert const1.is_dimensionless
    assert const2.is_dimensionless


def test_symbolic():
    const1 = Constant('A')
    const2 = Constant('1/2')

    assert const1._symbolic == Symbol(_prettify_name('A', bold=True))
    assert const2._symbolic == Number(1,2)


def test_dependent_and_scaling_attributes():
    const1 = Constant('A')
    const2 = Constant(-3)

    assert not const1.is_dependent
    assert not const2.is_dependent
    assert not const1.is_scaling
    assert not const2.is_scaling


def test_attributes():
    const1 = Constant('A')
    const2 = Constant(-3)
    const3 = Constant(1/2)
    const4 = Constant('sqrt(2)/2')
    const5 = Constant('sqrt(2)/pi')
    const6 = One()

    assert const1._is_constant
    assert not const1._is_number
    assert not const1._is_quotient
    assert not const1._is_one

    assert const2._is_constant
    assert const2._is_number
    assert not const2._is_quotient
    assert not const2._is_one

    assert const3._is_constant
    assert const3._is_number
    assert const3._is_quotient
    assert not const3._is_one

    assert const4._is_constant
    assert const4._is_number
    assert const4._is_quotient
    assert not const4._is_one

    assert const5._is_constant
    assert const5._is_number
    assert const5._is_quotient
    assert not const5._is_one

    assert const6._is_constant
    assert const6._is_number
    assert not const6._is_quotient
    assert const6._is_one


def test_multiplication():
    const1 = Constant('A')
    const2 = Constant(2/3)
    const3 = Constant(9)

    assert const1*const2 == Product(const2, const1)
    assert const2*const3 == Constant(6)


def test_exponentiation():
    const1 = Constant('A')
    const2 = Constant(2/3)

    assert const1**2 == Power(const1, 2)
    assert const2**-3 == Constant(27/8)


def test_division():
    const1 = Constant('A')
    const2 = Constant(2/3)
    const3 = Constant(2)

    assert const1/const2 == Product(Power(const2,-1), const1)
    assert const2/const3 == Constant(1/3)


def test_sympify():
    const1 = Constant('A')
    const2 = Constant(2/3)
    const3 = Constant(1)

    assert sympify(const1) == Symbol(_prettify_name('A', bold=True))
    assert sympify(const2) == Number(2,3)
    assert sympify(const3) == Number(1)


def test_sympyrepr():
    const1 = Constant('A')
    const2 = Constant(-3)
    const3 = Constant(1/2)
    const4 = One()

    assert srepr(const1) == "Constant('A')"
    assert srepr(const2) == 'Constant(-3)'
    assert srepr(const3) == 'Constant((1, 2))'
    assert srepr(const4) == 'One()'


def test_sympystr():
    const1 = Constant('A')
    const2 = Constant(-3)
    const3 = Constant(1/2)
    const4 = One()

    assert str(const1) == '𝐀'
    assert str(const2) == '-3'
    assert str(const3) == '1/2'
    assert str(const4) == '1'


def test_latex():
    const1 = Constant('A')
    const2 = Constant(-3)
    const3 = Constant(1/2)
    const4 = One()

    assert latex(const1) == '𝐀'
    assert latex(const2) == '-3'
    assert latex(const3) == '\\frac{1}{2}'
    assert latex(const4) == '1'


def test_pretty():
    const1 = Constant('A')
    const2 = Constant(-3)
    const3 = Constant(1/2)
    const4 = One()

    assert pretty(const1) == '𝐀'
    assert pretty(const2) == '-3'
    assert pretty(const3) == '1/2'
    assert pretty(const4) == '1'


def test_one():
    one1 = Constant(1)
    one2 = Constant('pi/pi')
    one3 = One()

    assert one1 == one2
    assert one2 == one3
    assert one1._is_one
    assert one2._is_one
    assert one3._is_one
