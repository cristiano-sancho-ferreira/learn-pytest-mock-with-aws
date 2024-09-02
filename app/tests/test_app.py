import pytest

def test_my_function_return_double():
    from src.double import Function
    actual_return = Function.my_function(x=5)

    assert actual_return == 10

def test_my_function_raise_when_x_is_not_int():
    from src.double import Function
    with pytest.raises(ValueError):
        Function.my_function(x="text")

    with pytest.raises(ValueError):
        Function.my_function(x=1.867857)