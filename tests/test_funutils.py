"""
Test Function Utility Module
"""
import numpy as np
import pytest
from xspline.funutils import (check_fun_input, check_number, shift_poly,
                              taylor_term)
from xspline.interval import Interval


@pytest.mark.parametrize(("data", "order"), [([1, 2, 3], -2),
                                             (np.random.randn(2, 3, 2), -2),
                                             (np.random.randn(5, 3), 2)])
def test_check_fun_input_error(data, order):
    with pytest.raises(AssertionError):
        check_fun_input(data, order)


@pytest.mark.parametrize(("data", "order"),
                         [([1, 2, 3], 1),
                          ([[1, 2, 3], [4, 5, 6]], -1),
                          ([[1, 2, 3], [4, 5, 6]], 0)])
def test_check_fun_input(data, order):
    data, order = check_fun_input(data, order)
    assert data.ndim == 2


@pytest.mark.parametrize(("data", "order", "result"),
                         ([[1], 0, 1],
                          [[2], 0, 1],
                          [[2], 1, 2],
                          [[2], 2, 2]))
def test_taylor_term(data, order, result):
    assert np.isclose(taylor_term(data, order), result)


@pytest.mark.parametrize("order", [0, 1, 2, 3])
def test_taylor_term_matrix(order):
    data = np.random.randn(2, 5)
    assert np.allclose(taylor_term(data, order),
                       taylor_term(data[1] - data[0], order))


@pytest.mark.parametrize("num", ["a", (1, 2), [1], {1}])
@pytest.mark.parametrize("num_type", [int])
def test_check_number_type(num, num_type):
    with pytest.raises(AssertionError):
        check_number(num, num_type)


@pytest.mark.parametrize("num", [1.0, 2.0, 3.0, 4.0])
@pytest.mark.parametrize("invl", [Interval(0.0, 0.5)])
def test_check_number_invl(num, invl):
    with pytest.raises(AssertionError):
        check_number(num, invl=invl)


@pytest.mark.parametrize("coefs", [np.random.randn(5) for i in range(5)])
@pytest.mark.parametrize("offset", [np.random.randn(10)])
@pytest.mark.parametrize("data", [np.linspace(-1.0, 1.0, 10)])
def test_shift_poly(coefs, offset, data):
    shifted_coefs = shift_poly(coefs, offset)
    assert np.allclose(np.polyval(coefs[::-1], data),
                       list(map(lambda c, d: np.polyval(c[::-1], d),
                                shifted_coefs, data - offset)))