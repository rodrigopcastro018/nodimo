from sympy import srepr, latex, pretty, Symbol, Pow, Mul, Number, sympify
from pytest import raises
from nodimo.dimension import Dimension
from nodimo.quantity import Quantity, Constant, One
from nodimo.product import Product
from nodimo.power import Power


def test_name():
    prod = Product(Quantity('a'), Quantity('b'), name='Pd')
    assert prod.name == 'Pd'


def test_factors():
    qty1 = Quantity('a', A=2, dependent=True)
    qty2 = Quantity('b', B=1)
    qty3 = Constant('c')
    prod = Product(qty1, qty2, qty3, scaling=True)
    
    assert frozenset(prod.factors) == frozenset((qty1, qty2, qty3))


def test_dimension():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Quantity('b', B=2)
    qty3 = Constant('c')
    qty4 = Quantity('d', C=5, scaling=True)
    prod = Product(qty1, qty2, qty3, qty4, scaling=True)

    assert prod.dimension == Dimension(A=2, B=1, C=11/2)


def test_factor_wrong_type():
    with raises(TypeError):
        Product(Quantity('a'), 123)


def test_no_factors():
    assert Product() == One()


def test_one_factor():
    qty = Quantity('a')
    assert Product(qty) is qty


def test_simplified_factors():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, 5)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    simplified_factors = frozenset((Constant((15625, 117649)), qty1**-2, qty2**-1))

    assert frozenset(prod1.factors) == simplified_factors
    assert frozenset(prod2.factors) == frozenset((qty1, qty2, qty3, pow1, pow2, pow3))


def test_attributes():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, 5)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    prod3 = Product(qty2, qty3, pow2, pow3)
    prod4 = Product(qty2, qty3, pow2, pow3, reduce=False)
    prod5 = Product(qty1, qty2, qty3, reduce=False)

    assert not prod1._is_power
    assert prod1._is_product
    assert prod1._is_derived
    assert not prod1._is_constant
    assert not prod1._is_number
    assert prod1._is_quotient
    assert prod1._is_reduced

    assert not prod2._is_power
    assert prod2._is_product
    assert prod2._is_derived
    assert not prod2._is_constant
    assert not prod2._is_number
    assert prod2._is_quotient
    assert not prod2._is_reduced

    assert not prod3._is_power
    assert prod3._is_product
    assert prod3._is_derived
    assert prod3._is_constant
    assert not prod3._is_number
    assert prod3._is_quotient
    assert prod3._is_reduced

    assert not prod4._is_power
    assert prod4._is_product
    assert prod4._is_derived
    assert prod4._is_constant
    assert not prod4._is_number
    assert prod4._is_quotient
    assert not prod4._is_reduced

    assert not prod5._is_power
    assert prod5._is_product
    assert prod5._is_derived
    assert not prod5._is_constant
    assert not prod5._is_number
    assert not prod5._is_quotient
    assert prod5._is_reduced


def test_unreduced():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, 5)
    prod = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)

    assert prod.reduce()._unreduced == prod


def test_reduce():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, 5)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    prod3 = prod2.reduce()

    assert prod3 == prod1
    assert prod3._unreduced == prod2


def test_symbolic():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, 5)
    pow4 = Power(pow1, -1, name='Pw')
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    prod3 = Product(qty2, qty3, pow2, pow3)
    prod4 = Product(qty2, qty3, pow2, pow3, reduce=False)
    prod5 = Product(pow4, qty2, reduce=False)
    prod6 = Product(qty1, qty2, qty3, pow1, pow2, pow3, scaling=True, name='Pd')

    assert prod1._symbolic == Mul(Number(15625, 117649), Pow(Symbol('a'), Number(-2)), Pow(Symbol('𝐜'), Number(-1)), evaluate=False)
    assert prod2._symbolic == Mul(Symbol('a'), Symbol('𝐜'), Number(-5, 7), Pow(Symbol('a'), Number(-3)), Pow(Symbol('𝐜'), Number(-2)), Number(-3125, 16807), evaluate=False)
    assert prod3._symbolic == Mul(Number(15625, 117649), Pow(Symbol('𝐜'), Number(-1)), evaluate=False)
    assert prod4._symbolic == Mul(Symbol('𝐜'), Number(-5, 7), Pow(Symbol('𝐜'), Number(-2)), Number(-3125, 16807), evaluate=False)
    assert prod5._symbolic == Mul(Symbol('Pw'), Symbol('𝐜'), evaluate=False)
    assert prod6._symbolic == Symbol('Pd')


def test_copy():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, 5)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    prod1_copy = prod1._copy()
    prod2_copy = prod2._copy()

    assert prod1_copy == prod1
    assert prod2_copy == prod2
    assert prod1_copy._unreduced == prod1._unreduced
    assert prod2_copy._unreduced == prod2._unreduced


def test_numerator_and_denominator_quantities():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, -2)
    pow1_inv = Power(qty1, 3)
    pow2_inv = Power(qty2, 2)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)

    assert prod1._numerator_quantities == [Constant(-7/5),]
    assert prod1._denominator_quantities == [Power(qty1, 2), qty2]
    assert prod2._numerator_quantities == [qty1, qty2, qty3, pow3]
    assert prod2._denominator_quantities == [pow1_inv, pow2_inv]


def test_sympify():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, -2)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3, scaling=True)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, dependent=True, reduce=False)
    sym1 = Mul(Number(-1), Number(7, 5), Pow(Symbol('a'), Number(-2)), Pow(Symbol('𝐜'), Number(-1)))
    sym2 = Mul(Symbol('a'), Symbol('𝐜'), Number(-5, 7), Pow(Symbol('a'), Number(-3)), Pow(Symbol('𝐜'), Number(-2)), Number(49, 25), evaluate=False)

    assert sympify(prod1) == sym1
    assert sympify(prod2) == sym2


def test_dependent_and_scaling():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    prod1 = Product(qty1, qty2, qty3, scaling=True)
    prod2 = Product(qty1, qty2, qty3, dependent=True)

    assert prod1.is_scaling
    assert not prod1.is_dependent
    assert not prod2.is_scaling
    assert prod2.is_dependent


def test_dimensionless_and_scaling():
    with raises(ValueError):
        qty1 = Quantity('a', dependent=True)
        qty2 = Constant('c')
        qty3 = Constant(-5/7)
        prod = Product(qty1, qty2, qty3, scaling=True)


def test_constant_and_dependent():
    qty1 = Constant('c')
    qty2 = Constant(-5/7)

    with raises(ValueError):
        prod = Product(qty1, qty2, dependent=True)
    
    with raises(ValueError):
        prod = Product(qty1, qty2)
        prod._is_dependent = True
        prod._validate_quantity()


def test_constant_and_scaling():
    qty1 = Constant('c')
    qty2 = Constant(-5/7)

    with raises(ValueError):
        prod = Product(qty1, qty2, scaling=True)
    
    with raises(ValueError):
        prod = Product(qty1, qty2)
        prod._is_scaling = True
        prod._validate_quantity()


def test_sympyrepr():
    qty1 = Quantity('a', A=2, B=-1, C=1/2, dependent=True)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, -2)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3, scaling=True)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, dependent=True, reduce=False)

    assert srepr(prod1) == "Product(Constant((-7, 5)), Power(Quantity('a', A=2, B=-1, C=(1, 2), dependent=True), -2), Power(Constant('c'), -1), scaling=True)"
    assert srepr(prod2) == "Product(Quantity('a', A=2, B=-1, C=(1, 2), dependent=True), Constant('c'), Constant((-5, 7)), Power(Quantity('a', A=2, B=-1, C=(1, 2), dependent=True), -3), Power(Constant('c'), -2), Constant((49, 25)), dependent=True, reduce=False)"


def test_sympystr():
    qty1 = Quantity('a', A=2, B=-1, C=1/2)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, -2)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    prod3 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False, name='Pd')
    prod4 = Product(qty1, qty2, qty3)
    prod5 = Product(qty1, qty2, pow1, Power(qty3, -1, reduce=False), pow2, reduce=False)
    prod6 = Product(qty1, Power(prod4, -1, reduce=False), reduce=False)

    assert str(prod1) == '(-7/5)/(a**2*𝐜)'
    assert str(prod2) == 'a*𝐜*(-5/7)*(49/25)/(a**3*𝐜**2)'
    assert str(prod3) == 'Pd'
    assert str(prod4) == '(-5/7)*a*𝐜'
    assert str(prod5) == 'a*𝐜/(a**3*(-5/7)*𝐜**2)'
    assert str(prod6) == 'a/((-5/7)*a*𝐜)'


def test_latex():
    qty1 = Quantity('a', A=2, B=-1, C=1/2)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, -2)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    prod3 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False, name='Pd')
    prod4 = Product(qty1, qty2, qty3)
    prod5 = Product(qty1, qty2, pow1, Power(qty3, -1, reduce=False), pow2, reduce=False)

    assert latex(prod1) == '\\frac{- \\frac{7}{5}}{{a}^{2} 𝐜}'
    assert latex(prod2) == '\\frac{a 𝐜 \\left(- \\frac{5}{7}\\right) \\frac{49}{25}}{{a}^{3} {𝐜}^{2}}'
    assert latex(prod3) == 'Pd'
    assert latex(prod4) == '- \\frac{5}{7} a 𝐜'
    assert latex(prod5) == '\\frac{a 𝐜}{{a}^{3} \\left(- \\frac{5}{7}\\right) {𝐜}^{2}}'


def test_pretty():
    qty1 = Quantity('a', A=2, B=-1, C=1/2)
    qty2 = Constant('c')
    qty3 = Constant(-5/7)
    pow1 = Power(qty1, -3)
    pow2 = Power(qty2, -2)
    pow3 = Power(qty3, -2)
    prod1 = Product(qty1, qty2, qty3, pow1, pow2, pow3)
    prod2 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False)
    prod3 = Product(qty1, qty2, qty3, pow1, pow2, pow3, reduce=False, name='Pd')
    prod4 = Product(qty1, qty2, qty3)
    prod5 = Product(qty1, qty2, pow1, Power(qty3, -1, reduce=False), pow2, reduce=False)

    assert pretty(prod1) == '-7/5\n────\n 2  \na ⋅𝐜'
    assert pretty(prod2) == '           49\na⋅𝐜⋅(-5/7)⋅──\n           25\n─────────────\n     3  2    \n    a ⋅𝐜     '
    assert pretty(prod3) == 'Pd'
    assert pretty(prod4) == '-5/7⋅a⋅𝐜'
    assert pretty(prod5) == '    a⋅𝐜     \n────────────\n 3         2\na ⋅(-5/7)⋅𝐜 '
