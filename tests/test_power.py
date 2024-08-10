from sympy import srepr, latex, pretty, Symbol, Pow, Number, sympify
from pytest import raises
from nodimo.dimension import Dimension
from nodimo.quantity import Quantity, Constant, One
from nodimo.product import Product
from nodimo.power import Power
from nodimo._internal import _prettify_name


def test_name():
    power = Power(Quantity('a'), -1/2, name='Pw')
    assert power.name == 'Pw'


def test_base_and_exponent():
    qty = Quantity('qty', B=3, scaling=True)
    pow1 = Power(qty, -55)
    pow2 = Power(pow1, -1/11)
    pow3 = Power(pow2, -1/5, reduce=False)

    assert pow1.base == qty
    assert pow1.exponent == Number(-55)
    assert pow2.base == qty
    assert pow2.exponent == Number(5)
    assert pow3.base == pow2
    assert pow3.exponent == Number(-1,5)


def test_dimension():
    qty1 = Quantity('qty1', A=1, B=-2, C=3/2)
    qty2 = Quantity('qty2', A=0, dependent=True)
    pow1 = Power(qty1, -2)
    pow2 = Power(qty2, 1/3)

    assert pow1.dimension == Dimension(A=-2, B=4, C=-3)
    assert pow2.dimension == Dimension()
    assert not pow1.is_dimensionless
    assert pow2.is_dimensionless


def test_base_wrong_type():
    with raises(TypeError):
        Power(123, 3)


def test_one_base():
    assert Power(One(), -5) == One()


def test_zero_exponent():
    assert Power(Quantity('a'), 0) == One()


def test_one_exponent():
    qty = Quantity('a')
    assert Power(qty, 1) is qty


def test_number_base():
    assert Power(Constant(3/2), 2) == Constant(9/4)


def test_power_base():
    assert Power(Power(Quantity('a'), -1/2), 2) == Power(Quantity('a'), -1)


def test_product_base():
    qty1 = Quantity('qty1', A=3, B=-1/2, C=5, scaling=True)
    qty2 = Quantity('qty2', A=-2, B=3/2, C=-4, dependent=True)
    prod = Product(qty1, qty2, scaling=True)
    power = Power(prod, -3, dependent=True)

    assert isinstance(power, Product)
    assert power.is_dependent
    assert not power.is_scaling


def test_attributes():
    qty1 = Quantity('a', A=2, scaling=True)
    qty2 = Constant(3/5)
    pow1 = Power(qty1, 2)
    pow2 = Power(qty2, -1.5)
    pow3 = Power(pow1, -1, reduce=False)

    assert pow1._is_power
    assert not pow1._is_product
    assert pow1._is_derived
    assert not pow1._is_constant
    assert not pow1._is_number
    assert not pow1._is_quotient
    assert pow1._is_reduced

    assert not pow2._is_power
    assert not pow2._is_product
    assert not pow2._is_derived
    assert pow2._is_constant
    assert pow2._is_number
    assert pow2._is_quotient
    assert pow2._is_reduced

    assert pow3._is_power
    assert not pow3._is_product
    assert pow3._is_derived
    assert not pow3._is_constant
    assert not pow3._is_number
    assert pow3._is_quotient
    assert not pow3._is_reduced


def test_symbolic():
    qty1 = Quantity('a', A=2, scaling=True)
    qty2 = Constant(3/5)
    pow1 = Power(qty1, -2)
    pow2 = Power(qty2, -1.5)
    pow3 = Power(pow1, -1, reduce=False)
    pow4 = Power(pow2, -1, reduce=False)
    pow5 = Power(pow1, 3, name='Pw')
    pow6 = Power(Constant('c'), 5, name='Pw')

    assert pow1._symbolic == Pow(Symbol('a'), Number(-2))
    assert pow2._symbolic == Pow(Number(3,5), Number(-3,2))
    assert pow3._symbolic == Pow(pow1._symbolic, -1, evaluate=False)
    assert pow4._symbolic == Pow(pow2._symbolic, -1)
    assert pow5._symbolic == Symbol('Pw')
    assert pow6._symbolic == Symbol(_prettify_name('Pw', bold=True))


def test_unreduced():
    qty1 = Quantity('qty1', dependent=True)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)

    assert pow2.base == pow1


def test_reduce():
    qty1 = Quantity('qty1', dependent=True)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)
    pow3 = pow2.reduce()

    assert pow3 == Power(pow1, -1/3)
    assert pow3._unreduced == pow2


def test_copy():
    qty1 = Quantity('qty1', dependent=True)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)
    pow3 = pow2.reduce()
    pow4 = Power(Product(qty1, pow1, pow2, pow3, reduce=False), 2, reduce=False)
    pow1_copy = pow1._copy()
    pow2_copy = pow2._copy()
    pow3_copy = pow3._copy()
    pow4_copy = pow4._copy()

    assert pow1_copy == pow1
    assert pow2_copy == pow2
    assert pow3_copy == pow3
    assert pow4_copy == pow4
    assert pow1_copy._unreduced == pow1._unreduced
    assert pow2_copy._unreduced == pow2._unreduced
    assert pow3_copy._unreduced == pow3._unreduced
    assert pow4_copy._unreduced == pow4._unreduced


def test_sympify():
    qty1 = Quantity('a', dependent=True)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)
    pow3 = Power(pow2, 3, name='Pw')
    sym1 = Pow(Symbol('a'), Number(-2), evaluate=False)
    sym2 = Pow(sym1, Number(-1,3), evaluate=False)
    sym3 = Symbol('Pw')

    assert sympify(pow1) == sym1
    assert sympify(pow2) == sym2
    assert sympify(pow3) == sym3


def test_dependent_and_scaling():
    qty1 = Quantity('qty1', A=2, scaling=True)
    qty2 = Quantity('qty2', B=3)
    qty3 = Quantity('qty3', dependent=True)
    pow1 = Power(qty1, -2, dependent=True)
    pow2 = Power(qty2, -1/2, scaling=True)
    pow3 = Power(qty3, 3, dependent=True)

    assert pow1.is_dependent
    assert not pow2.is_dependent
    assert pow3.is_dependent
    assert not pow1.is_scaling
    assert pow2.is_scaling
    assert not pow3.is_scaling

    with raises(ValueError):
        Power(qty1, -2, scaling=True, dependent=True)


def test_dimensionless_and_scaling():
    with raises(ValueError):
        Power(Quantity('a', dependent=True), 3, scaling=True)


def test_constant_and_dependent():
    with raises(ValueError):
        Power(Constant(-2), -2, dependent=True, reduce=False)
    
    with raises(ValueError):
        power = Power(Constant(-2), -2, reduce=False)
        power._is_dependent = True
        power._validate_quantity()


def test_constant_and_scaling():
    with raises(ValueError):
        Power(Constant(-2), -2, scaling=True, reduce=False)
    
    with raises(ValueError):
        power = Power(Constant(-2), -2, reduce=False)
        power._is_scaling = True
        power._validate_quantity()


def test_sympyrepr():
    qty1 = Quantity('qty1', dependent=True)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)

    assert srepr(pow1) == "Power(Quantity('qty1', dependent=True), -2)"
    assert srepr(pow2) == "Power(Power(Quantity('qty1', dependent=True), -2), (-1, 3), reduce=False)"


def test_sympystr():
    qty1 = Quantity('a', dependent=True)
    qty2 = Constant(55)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)
    pow3 = Power(pow2, 3, name='Pw')
    pow4 = Power(qty2, 8, reduce=False)
    pow5 = Power(Power(qty2, 1/2), 3, reduce=False)
    pow6 = Power(qty1, -1, reduce=False)
    pow7 = Power(qty1, 'sqrt(2)')

    assert str(pow1) == '1/a**2'
    assert str(pow2) == '1/(1/a**2)**(1/3)'
    assert str(pow3) == 'Pw'
    assert str(pow4) == '55**8'
    assert str(pow5) == '(sqrt(55))**3'
    assert str(pow6) == '1/a'
    assert str(pow7) == 'a**(sqrt(2))'


def test_latex():
    qty1 = Quantity('a', dependent=True)
    qty2 = Constant(55)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)
    pow3 = Power(pow2, 3, name='Pw')
    pow4 = Power(qty2, 8, reduce=False)
    pow5 = Power(Power(qty2, 1/2), 3, reduce=False)
    pow6 = Power(qty1, -1, reduce=False)

    assert latex(pow1) == '\\frac{1}{{a}^{2}}'
    assert latex(pow2) == (
        '\\frac{1}{{\\left(\\frac{1}{{a}^{2}}\\right)}^{\\frac{1}{3}}}'
    )
    assert latex(pow3) == 'Pw'
    assert latex(pow4) == '{55}^{8}'
    assert latex(pow5) == '{\\left(\\sqrt{55}\\right)}^{3}'
    assert latex(pow6) == '\\frac{1}{a}'


def test_pretty():
    qty1 = Quantity('a', dependent=True)
    qty2 = Constant(55)
    pow1 = Power(qty1, -2)
    pow2 = Power(pow1, -1/3, reduce=False)
    pow3 = Power(pow2, 3, name='Pw')
    pow4 = Power(qty2, 8, reduce=False)
    pow5 = Power(Power(qty2, 1/2), 3, reduce=False)
    pow6 = Power(qty1, -1, reduce=False)

    assert pretty(pow1) == '1 \n──\n 2\na '
    assert pretty(pow2) == (
        '   1   \n───────\n    1/3\n⎛1 ⎞   \n⎜──⎟   \n⎜ 2⎟   \n⎝a ⎠   '
    )
    assert pretty(pow3) == 'Pw'
    assert pretty(pow4) == '  8\n55 '
    assert pretty(pow5) == '     3\n(√55) '
    assert pretty(pow6) == '1\n─\na'
