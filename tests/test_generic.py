import sympy as sp
from sympy.physics.control import lti

import penbegone as pbg


def test_linearization():
    """Test the linearization of a nonlinear function."""
    x = sp.symbols("s")
    f_ = x**2
    f_lin_ = pbg.common.linearize(f_, x, x_0=2)
    f_lin_exp_ = 4 * x - 4
    assert f_lin_ - f_lin_exp_ == 0


def test_ilaplace():
    """Test the inverse Laplace transform."""
    s, t, a = sp.symbols("s t a")
    Y_ = 1 / (s + a)
    y_ = pbg.common.ilaplace(Y_, s, t)
    y_exp_ = sp.exp(-a * t) * sp.Heaviside(t)
    assert y_ - y_exp_ == 0


def test_final_value_time():
    """Test the final value in the time domain."""
    t = sp.symbols("t")
    f_ = 1 - 1.6 * sp.exp(-10 * t) + 0.6 * sp.exp(-20 * t)
    assert pbg.common.final_value_time(f_, t) == 1


def test_unit_feedback_tf():
    """Test unit feedback with TF."""
    s = sp.symbols("s")
    G = lti.TransferFunction(1, s, s)
    H_ = pbg.common.feedback(G)
    assert H_.to_expr() - 1 / (s + 1) == 0


def test_equations_solve():
    """Test the equations solve() method."""
    x1, x2 = sp.symbols("x_1, x_2")
    eqs = pbg.common.Equations()
    eqs.add(x1, 2 * x2)
    eqs.add(x2, x1 + 1)
    sols = eqs.solve()
    assert sols[x1] + 2 == 0
    assert sols[x2] + 1 == 0
