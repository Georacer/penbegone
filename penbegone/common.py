import functools
import operator

import IPython as ip
import sympy as sp
from sympy.physics.control import lti

# Conventions
# A: sympy symbol
# A_: expression
# A__: evaluated expression or symbol
#
# Use `display` to print symbols


def printeq(lht, rht):
    """Print the two parts of an equation in the jupyter output."""
    try:
        ip.display.display(sp.Eq(lht, rht, evaluate=False))
    except BaseException:
        ip.display.display(lht)
        print("=")
        ip.display.display(rht)


def printsols(sols):
    """Print the solutions coming out of a solve() method."""
    for lhs, rhs in sols.items():
        printeq(lhs, rhs)


class Equations:
    """A system of equations."""

    def __init__(self):
        """Class constructor."""
        self.r_values = {}  # Left-hand variable values.
        self.eqs = {}
        self.values = {}
        self._counter = 0
        self._last_shown = 0

    def __getitem__(self, key):
        """Return an equation from the set."""
        return self.eqs[key]

    def add(self, left, right):
        """Add an equation to the system."""
        # Add an equation to the list
        self._add(left, right)

    def _add(self, left, right, silent=False):
        if silent:
            key = "temp"
        else:
            key = self._counter + 1
            self._counter += 1
        self.eqs[key] = -left + right
        self.r_values[key] = left

    def set_value(self, var, value):
        """Substitute a variable for its value in the whole equation set."""
        self.values[var] = value

    def isolate(self, key, variable, display=True):
        """Isolave an equation for a variable."""
        self.add(variable, sp.solve(self.eqs[key], variable)[0])
        del self.r_values[key]
        del self.eqs[key]

        # Print the new equations.
        if display:
            self.show()

    def update(self, key, variable, display=True):
        """Solve an equation for a variable and re-apply it to the whole set.

        Does not delete the equation."""
        old_eqs = dict(self.eqs)
        old_r_values = self.r_values
        solution = sp.solve(old_eqs[key], variable)[0]
        self.eqs = {}
        self.r_values = {}

        old_keys = old_eqs.keys()
        for old_key in old_keys:
            if variable in old_eqs[old_key].free_symbols:
                # This equation involves the variable.
                r_value = old_r_values[old_key]
                r_expr = old_eqs[old_key] + r_value
                self.add(r_value, sp.cancel(r_expr.subs([(variable, solution)])))
            else:
                # This is an unrelated equation, ignore it.
                self.eqs[old_key] = old_eqs[old_key]
                self.r_values[old_key] = old_r_values[old_key]
        self.values[variable] = solution

        # Print the new equations.
        if display:
            self.show()

    def use_eq(self, key, variable, display=True):
        """Solve an equation for a variable and substitute it in the whole set.

        This also deletes this equation from the set, to avoid using it again.
        (The selected equation will be substituted by a 0 expression).
        """
        old_eqs = dict(self.eqs)
        old_r_values = self.r_values
        solution = sp.solve(old_eqs[key], variable)[0]
        self.eqs = {}
        self.r_values = {}

        del old_eqs[key]
        keys = old_eqs.keys()
        for old_key in keys:
            if variable in old_eqs[old_key].free_symbols:
                # If this is a newly substituted equation
                r_value = old_r_values[old_key]
                if variable == r_value:
                    # The r_value is about to be substituted
                    self.add(0, sp.cancel(old_eqs[old_key].subs([(variable, solution)])))
                else:
                    r_expr = old_eqs[old_key] + r_value
                    self.add(r_value, sp.cancel(r_expr.subs([(variable, solution)])))
            else:
                self.eqs[old_key] = old_eqs[old_key]
                self.r_values[old_key] = old_r_values[old_key]
        self.values[variable] = solution

        # Print the new equations.
        if display:
            self.show()

    def apply(self, variable, expression):
        """Equivalent of adding an equation and calling use_eq on it."""
        self._add(variable, expression, silent=True)
        self.use_eq("temp", variable)

    def show(self, show_all=False):
        """Show the whole equation set.

        By default will show only equations not previously shown.

        Args:
            show_all: Show all the equations of the set.
        """
        sorted_keys = sorted(self.eqs.keys())
        for key in sorted_keys:
            if key > self._last_shown or show_all:
                r_value = self.r_values[key]
                expr = sp.simplify(self.eqs[key] + r_value)
                string = ip.display.Markdown(f"[{key}]: ${sp.printing.latex(r_value)}$ = ${sp.printing.latex(expr)}$")
                ip.display.display(string)

        self._last_shown = sorted_keys[-1]

    def solve(self, variables=None):
        """Attempt to solve the equation system automatically."""
        if not variables:
            variables = list(self.r_values.values())
        sols = sp.solve(self.eqs.values(), variables, check=False, warning=True)
        return {k: sp.simplify(v) for k, v in sols.items()}


def linearize(f, x=None, x_0=0):
    """Linearize a symbolic expression.

    Args:
        f: A nonlinear symbolic expression.
        x: The variable to linearize for.
        x_0: The linearization point.

    Returns:
        A symbolic expression.

    Employs: https://docs.sympy.org/latest/modules/series/series.html#more-intuitive-series-expansion
    """
    res = sp.series(f, x, x_0, n=2)
    res = res.removeO()  # Drop the remainder terms.
    return res


def tf(num, den, var):
    """Create an LTI system.

    Args:
        num: Numerator polynomial
        den: Denominator polynomial
        var: The TF variable.

    """
    return lti.TransferFunction(num, den, var)


def series(*args):
    """Return the series combination of SISO systems.

    Args:
        Can be either sympy.physics.control.lti.SISOLinearTimeInvariant or symbol.
    """
    if isinstance(args[0], sp.physics.control.lti.SISOLinearTimeInvariant):
        return lti.Series(*args, evaluate=True)
    else:
        return functools.reduce(operator.mul, args, 1)


def parallel(*args):
    """Return the parallel combination of SISO systems."""
    if isinstance(args[0], sp.physics.control.lti.SISOLinearTimeInvariant):
        return lti.Parallel(*args, evaluate=True)
    else:
        return functools.reduce(operator.add, args, 0)


def feedback(sys1, sys2=None, sign=-1):
    """Return the feedback combination of two SISO systems."""
    if isinstance(sys1, sp.physics.control.lti.SISOLinearTimeInvariant):
        if not sys2:
            sys2 = lti.TransferFunction(1, 1, sp.symbols("s"))
        return lti.Feedback(sys1, sys2, sign).doit(cancel=True)
    else:
        if not sys2:
            sys2 = 1
        return sp.simplify(sys1 / (1 - sign * sys1 * sys2))


def ilaplace(expr, s, t):
    """Calculate the inverse Laplace transform of an expression.

    Args:
        expr: The expression.
        s: The frequency-domain variable.
        t: The time-domain variable
    """
    return sp.inverse_laplace_transform(expr, s, t)


def final_value_time(expr, t):
    """Find the final value of an expresssion in the time domain.

    Args:
        expr: The expression
        t: The time variable.
    """
    return sp.limit(expr, t, sp.oo)


def final_value_freq(expr, s):
    """Find the final value of an expresssion in the frequency domain.

    Args:
        expr: The expression
        s: The frequency variable.
    """
    return sp.limit(s * expr, s, 0)


if __name__ == "__main__":  # pragma: no cover
    pass
