from sympy import srepr
from pytest import raises
from nodimo.quantity import Quantity
from nodimo.groups import ScalingGroup
from nodimo.relation import Relation
from nodimo.model import Model


def test_scaling_groups():
    a = Quantity('a', A=2, B=-1, dependent=True)
    b = Quantity('b', A=1, scaling=True)
    c = Quantity('c', A=-2, B=2, scaling=True)
    d = Quantity('d', A=2, scaling=True)
    md = Model(a, b, c, d)

    assert md._scaling_groups == [ScalingGroup(b,c), ScalingGroup(c,d)]


def test_unique_relation():
    a = Quantity('a', A=2, B=-1, dependent=True)
    b = Quantity('b', A=1, scaling=True)
    c = Quantity('c', A=-2, B=2, scaling=True)
    d = Quantity('d', B=2)
    md = Model(a, b, c, d)

    prod1 = a*c**(1/2)/b
    prod2 = d/(b**2*c)
    prod1._is_dependent = True

    assert md.relations[md._scaling_groups[0]] == Relation(prod1, prod2, name='Phi')


def test_scaling_groups_and_relations():
    a = Quantity('a', A=2, B=-1, dependent=True)
    b = Quantity('b', A=1, scaling=True)
    c = Quantity('c', A=-2, B=2, scaling=True)
    d = Quantity('d', B=2, scaling=True)
    md = Model(a, b, c, d)
    sg1 = ScalingGroup(b,c)
    sg2 = ScalingGroup(b,d)
    sg3 = ScalingGroup(c,d)

    assert md._scaling_groups == [sg1, sg2, sg3]

    prod11 = a*c**(1/2)/b
    prod12 = d/(b**2*c)
    prod11._is_dependent = True

    prod21 = a*d**(1/2)/b**2
    prod22 = c*b**2/d
    prod21._is_dependent = True

    prod31 = a*c/d**(1/2)
    prod32 = b*c**(1/2)/d**(1/2)
    prod31._is_dependent = True

    assert md.relations[sg1] == Relation(prod11, prod12, name='Phi_1')
    assert md.relations[sg2] == Relation(prod21, prod22, name='Phi_2')
    assert md.relations[sg3] == Relation(prod31, prod32, name='Phi_3')


def test_model_validation():
    a = Quantity('a', A=2, B=-1, dependent=True)
    b = Quantity('b', A=1)
    c = Quantity('c', A=-2, B=2)
    d = Quantity('d', B=2)
    
    with raises(ValueError):
        Model(a, b, c, d)


def test_show(capfd):
    a = Quantity('a', A=2, B=-1, dependent=True)
    b = Quantity('b', A=1, scaling=True)
    c = Quantity('c', A=-2, B=2, scaling=True)
    d = Quantity('d', B=2, scaling=True)
    md = Model(a, b, c, d)
    md.show()
    out, _ = capfd.readouterr()
    assert out == (
        '\n'
        'a = f(b, c, d)\n'
        '\n'
        '------------------------------------------------------------------------------\n'
        '\n'
        'Scaling group 1 (b, c)\n'
        '\n'
        '\n'
        '   1/2           \n'
        'a⋅c        ⎛ d  ⎞\n'
        '────── = Φ₁⎜────⎟\n'
        '  b        ⎜ 2  ⎟\n'
        '           ⎝b ⋅c⎠\n'
        '\n'
        '------------------------------------------------------------------------------\n'
        '\n'
        'Scaling group 2 (b, d)\n'
        '\n'
        '\n'
        '   1/2     ⎛   2⎞\n'
        'a⋅d        ⎜c⋅b ⎟\n'
        '────── = Φ₂⎜────⎟\n'
        '   2       ⎝ d  ⎠\n'
        '  b              \n'
        '\n'
        '------------------------------------------------------------------------------\n'
        '\n'
        'Scaling group 3 (c, d)\n'
        '\n'
        '\n'
        '         ⎛   1/2⎞\n'
        'a⋅c      ⎜b⋅c   ⎟\n'
        '──── = Φ₃⎜──────⎟\n'
        ' 1/2     ⎜  1/2 ⎟\n'
        'd        ⎝ d    ⎠\n'
        '\n'
    )


def test_equality():
    a = Quantity('a', A=2, B=-1, dependent=True)
    b = Quantity('b', A=1, scaling=True)
    c = Quantity('c', A=-2, B=2, scaling=True)
    d = Quantity('d', B=2)
    md1 = Model(a, b, c, d, A=3)
    md2 = Model(b, d, c, a, A=3)
    md3 = Model(b, d, c, a, A=-1)

    assert md1 == md2
    assert md1 != md3


def test_sympyrepr():
    a = Quantity('a', A=2, B=-1, dependent=True)
    b = Quantity('b', A=1, scaling=True)
    c = Quantity('c', A=-2, B=2, scaling=True)
    d = Quantity('d', B=2, scaling=True)
    md1 = Model(a, b, c, d)
    md2 = Model(a, b, c, d, A=1, B='-sqrt(2)')

    assert srepr(md1) == "Model(Quantity('a', A=2, B=-1, dependent=True), Quantity('b', A=1, scaling=True), Quantity('c', A=-2, B=2, scaling=True), Quantity('d', B=2, scaling=True))"
    assert srepr(md2) == "Model(Quantity('a', A=2, B=-1, dependent=True), Quantity('b', A=1, scaling=True), Quantity('c', A=-2, B=2, scaling=True), Quantity('d', B=2, scaling=True), A=1, B='-sqrt(2)')"
