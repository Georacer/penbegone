import sympy as sp

import penbegone as pbg


def test_linearization():
    """Test the linearization of a nonlinear function."""
    x = sp.symbols("s")
    f_ = x**2
    f_lin_ = pbg.common.linearize(f_, x, x_0=2)
    f_lin_exp_ = 4 * x - 4
    assert f_lin_ - f_lin_exp_ == 0
