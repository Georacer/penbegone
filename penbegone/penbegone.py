import IPython as ip
import sympy as sp

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


class Equations:
    """A system of equations."""

    def __init__(self):
        """Class constructor."""
        self.r_values = {}
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

    def use_eq(self, key, variable):
        """Solve an equation for a variable and substitute it in the whole set.

        This also deletes this equation from the set, to avoid using it again.
        (The selected equation will be substituted by an 0 expression).
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

    def solve(self, variables):
        """Attempt to solve the equation system automatically."""
        return sp.solve(self.eqs.values(), variables, check=False, warning=True)


def linearize(f, x=None, x_0=0):
    """Linearize a symbolic expression.

    Args:
        f: A nonlinear symbolic expression.
        x: The variable to linearize for.
        x_0: The linearization point.

    Employs: https://docs.sympy.org/latest/modules/series/series.html#more-intuitive-series-expansion
    """
    res = sp.series(f, x, x_0, n=2)
    res = res.removeO()  # Drop the remainder terms.
    return res


if __name__ == "__main__":  # pragma: no cover
    pass
