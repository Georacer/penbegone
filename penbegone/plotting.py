import sympy as sp
from sympy.physics.control.lti import TransferFunction


def pole_zero(sys, s=None):
    """Draw the pole-zero plot of a system.

    Args
    ----
    sys: sympy.physics.control.lti.TransferFunction, sympy expression
        The system to plot.
    s:
        The sympy variable that represents the complex frequency
    """

    if not isinstance(sys, TransferFunction):
        sys = TransferFunction(sp.numer(sys), sp.denom(sys), s)
    sp.physics.control.control_plots.pole_zero_plot(sys, grid=True)
