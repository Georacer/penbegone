import sympy as sp
from matplotlib import style

style.use("ggplot")  # Enable grid plotting.


def plot_pole_zero(sys):
    """Draw the pole-zero plot of a system."""
    sp.physics.control.control_plots.pole_zero_plot(sys)
