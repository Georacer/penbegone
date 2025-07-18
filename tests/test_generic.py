import sympy as sp
from sympy.physics.control import lti

import penbegone as pbg


def test_find_functions():
    """Test the find_functions function."""
    x, y = sp.symbols("x y")
    f, g = pbg.common.functions("f g", x)
    h = pbg.common.functions("h", y)
    expr_ = f + g + h
    funs = pbg.common.find_functions(expr_, x)
    assert f.func in funs
    assert g.func in funs
    assert h.func not in funs


def test_linearization():
    """Test the linearization of a nonlinear function."""
    x = sp.symbols("x")
    f_ = x**2
    f_lin_ = pbg.common.linearize(f_, x, x_0=2)
    f_lin_exp_ = 4 * (x - 2) + f_.subs(x, 2)
    assert f_lin_ - f_lin_exp_ == 0


def test_linearization_2():
    """Test the linearization of a nonlinear function into a local model"""
    x, c = sp.symbols("x c")
    f_ = c * sp.ln(x)
    f_lin_ = pbg.common.linearize(f_, x, x_0=2, local_model=True)
    f_lin_exp_ = c / 2 * (x)
    assert f_lin_ - f_lin_exp_ == 0


def test_linearization_3():
    """Test a vector, multivariate function."""
    x, y = sp.symbols("x y")
    f1_ = x**2 + y**2
    f2_ = x * y
    f_ = [f1_, f2_]
    variables = [x, y]
    init_conds = [1, 1]
    f_lin_ = pbg.common.linearize(f_, variables, init_conds)
    assert len(f_lin_) == 2
    assert f_lin_[0] - (2 * x + 2 * y - 2) == 0
    assert f_lin_[1] - (x + y - 1) == 0


def test_laplace():
    """Test the Laplace transform."""
    s, t, a = sp.symbols("s t a")
    y_ = sp.exp(-a * t)
    Y_ = pbg.common.laplace(y_, t, s)
    Y_exp_ = 1 / (s + a)
    assert Y_ - Y_exp_ == 0


def test_laplace_2():
    """Test the Laplace transform when using functions."""
    s, t = sp.symbols("s t")
    f = pbg.common.functions("f", t)
    F = pbg.common.functions("F", s)
    corr = {f.func: F.func}
    y_ = t * f
    Y_ = pbg.common.laplace(y_, t, s, corr)
    Y_exp_ = -F.diff(s)
    assert Y_ - Y_exp_ == 0


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


def test_equations_rearrange():
    """Test the equations rearrange() method.

    When r_value == variable, it does nothing."""
    x1, x2 = sp.symbols("x_1, x_2")
    eqs = pbg.common.Equations()
    eqs.add(3 * x2 - x1, x1)
    eqs.add(x2, x1 + 1)
    eqs.rearrange(1, x1)  # Called with inplace = False
    assert len(eqs.eqs) == 2  # There are still two equations.
    assert eqs._counter == 3  # A new equation has been created.
    assert 1 not in eqs  # The old one has been deleted.
    assert eqs.lht[2] - x2 == 0
    assert eqs.rht[2] - x1 - 1 == 0
    assert eqs.lht[3] - x1 == 0
    assert eqs.rht[3] - (3 / 2 * x2) == 0


def test_equations_use_eq():
    """Test the equations use_eq() method.

    When r_value == variable, it does nothing."""
    x1, x2 = sp.symbols("x_1, x_2")
    eqs = pbg.common.Equations()
    eqs.add(x1, 2 * x2)
    eqs.add(x2, x1 + 1)
    eqs.use_eq(1, x1)
    assert len(eqs) == 2  # We should have one equation left and one solution.
    assert 1 not in eqs
    assert 2 not in eqs
    assert 3 in eqs
    assert eqs.solutions[x1] - 2 * x2 == 0
    assert eqs.lht[3] - x2 == 0
    assert eqs.rht[3] - (2 * x2 + 1) == 0
