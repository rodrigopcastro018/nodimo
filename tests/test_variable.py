from nodimo import Variable

def test_nondimensional_variable():
    ndvar1 = Variable('ndvar1')
    ndvar2 = Variable('ndvar2', D1=0, D2=0, D3=0, D4=0, D5=0)

    assert ndvar1.is_nondimensional
    assert ndvar2.is_nondimensional