import collections
import functools
import operator
from copy import copy

import IPython as ip
import sympy as sp
from sympy.physics.control import lti

# Conventions
# A: sympy symbol
# A_: expression
# A__: evaluated expression or symbol
#
# Use `display` to print symbols


class NoSolutionError(RuntimeError):
    def __init__(self):
        super().__init__("Could not find a solution.")


def functions(definitions, arg):
    """Define function variables.

    Args
    ----
    definitions : str
        Same as the argument of sp.symbols(definitions)
    arg : sp.Symbol
        The single argument to the function. E.g. x for f(x).
    """
    funs = sp.symbols(definitions, cls=sp.Function)
    if isinstance(funs, collections.abc.Iterable):
        return [fun(arg) for fun in funs]
    else:
        return funs(arg)


def find_functions(expr, arg=None, pure=True):
    """Find all the functions in an expression.

    Args
    ----
    expr
        A sympy expression.
    arg : sp.Symbol, optional
        Return functions of that argument only. E.g. Return f only if f(x).
    pure : bool
        If True, return only f. If False, return f(arg).

    Returns
    -------
    functions : Iterable
        The functions found in the expression.
    """

    if arg:
        functions = {
            i for i in expr.atoms(sp.Function) if isinstance(i, sp.core.function.AppliedUndef) and i.args == (arg,)
        }
    else:
        functions = set(expr.atoms(sp.Function))
    if pure:
        functions = {i.func for i in functions}
    return functions


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
        self.lht = {}  # Left-hand equation terms. For display purposes only.
        self.rht = {}  # Right-hand equation terms. For display purposes only.
        self.eqs = {}  # The equations still being used to solve the system.
        self.solutions = {}  # Dictionary with solutions, as variable:value entries.
        self.solutions_updated = {}  # Dictionary with self.solutions.keys() and a bool on whether it's been printed.
        self._counter = 0  # The number of the last-created equation.
        self._last_shown = 0

    def __getitem__(self, key):
        """Return an equation from the set."""
        return self.eqs[key]

    def __contains__(self, key):
        """Tell if an equation key is found in this set."""
        return key in self.eqs

    def __delitem__(self, key):
        """Delete an equation."""
        del self.lht[key]
        del self.rht[key]
        del self.eqs[key]

    def __len__(self):
        """Tell how many equations are contained."""
        return len(self.eqs) + len(self.solutions)

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
        self.lht[key] = left
        self.rht[key] = right
        self.eqs[key] = -left + right

    def rearrange(self, key, variable, display=True, inplace=False):
        """Rearrange an equation for a variable.

        Perhaps it works for rearranging for an expression as well?"""
        solution = sp.solve(self.eqs[key], variable)[0]

        if inplace:
            self.lht[key] = variable
            self.rht[key] = solution
            self.eqs[key] = -variable + solution
        else:
            self.add(variable, solution)
            del self[key]

        # Print the new equations.
        if display:
            self.show()

    def use_eq(self, key, variable, display=True, force=False):
        """Solve an equation for a variable.

        Removes the equation and adds the variable to the solutions dictionary."""

        # Solve the equation for the variable.
        self.rearrange(key, variable, inplace=True, display=False)

        # Add the entry to the solutions attribute.
        self.solutions[variable] = self.rht[key]
        self.solutions_updated[variable] = True

        # Remove the equation.
        del self[key]

        # Update all involved equations with the new solutions entry.
        old_keys = list(self.eqs.keys())
        for old_key in old_keys:
            lht = self.lht[old_key]
            try:
                do_lht = variable in lht.free_symbols or variable in find_functions(lht, pure=False) or force
            except AttributeError:  # lht is probably a pure number.
                do_lht = False
            rht = self.rht[old_key]
            try:
                do_rht = variable in rht.free_symbols or variable in find_functions(rht, pure=False) or force
            except AttributeError:  # rht is probably a pure number.
                do_lht = False
            eq = self.eqs[old_key]
            do_eq = variable in eq.free_symbols or variable in find_functions(eq, pure=False) or force

            if do_eq:
                # This check doesn't work for symbols that are functions.
                eq = sp.simplify(eq.subs(variable, self.solutions[variable]))

                if do_lht:
                    lht = sp.simplify(lht.subs(variable, self.solutions[variable]))

                if do_rht:
                    rht = sp.simplify(rht.subs(variable, self.solutions[variable]))

                del self[old_key]
                self.add(lht, rht)

        # Update all involved solutions with the new solutions entry.
        for k, v in self.solutions.items():
            if (
                (k - variable != 0)  # This solution is not the one we just added.
                and (variable in v.free_symbols)  # The variable is involved in this solution;
                # It is worth substituting.
            ):
                self.solutions[k] = v.subs(variable, self.solutions[variable])
                self.solutions_updated[k] = False

        # Print the new equations.
        if display:
            self.show()

    def apply(self, variable, expression):
        """Equivalent of adding an equation and calling use_eq on it."""
        self._add(variable, expression, silent=True)
        self.use_eq("temp", variable)

    def apply_solutions(self, key, display=True):
        """Forcefully apply the solutions onto an equation."""
        lht = sp.simplify(self.lht[key].subs(self.solutions))
        rht = sp.simplify(self.rht[key].subs(self.solutions))

        del self[key]
        self.add(lht, rht)

    def update_solutions(self, var, display=True):
        """Apply a solution onto the rest."""
        for v, _ in self.solutions.items():
            if v - var != 0:
                self.solutions[v] = sp.simplify(self.solutions[v].subs(var, self.solutions[var]))
                self.solutions_updated[v] = True

        if display:
            self.show()

    def show(self, show_all=False):
        """Show the whole equation set.

        By default will show only equations and solutions not previously shown.

        Args:
            show_all: Show all the equations of the set.
        """
        # First show the solutions so far.
        variables = self.solutions_updated.keys()
        for var in variables:
            if self.solutions_updated[var] or show_all:
                string = ip.display.Markdown(f"${sp.printing.latex(var)}$ = ${sp.printing.latex(self.solutions[var])}$")
                ip.display.display(string)
                self.solutions_updated[var] = False

        # Next show the equations.
        sorted_keys = sorted(self.eqs.keys())
        for key in sorted_keys:
            if key > self._last_shown or show_all:
                string = ip.display.Markdown(
                    f"[{key}]: ${sp.printing.latex(self.lht[key])}$ = ${sp.printing.latex(self.rht[key])}$"
                )
                ip.display.display(string)

        if sorted_keys:
            self._last_shown = sorted_keys[-1]

    def solve(self, variables=None):
        """Attempt to solve the equation system automatically."""
        if not variables:
            variables = list(self.lht.values())
        sols = sp.solve(self.eqs.values(), variables, check=False, warning=True, dict=True)
        if not sols:
            raise NoSolutionError()
        return {k: sp.simplify(v) for k, v in sols[0].items()}

    def laplace(self, t, s, corr, show=True):
        """Carry out the Laplace transform to the whole set.

        Args
        ----
        t: sp.symbol
            The variable of time.
        s: sp.symbol
            The variable of frequency.
        corr: dict
            The correspondence between time and frequency functions. See build_correspondence.
        """

        # Carry out the transform in all equations.
        old_keys = list(self.eqs.keys())
        for old_key in old_keys:
            new_lht = laplace(self.lht[old_key], t, s, corr)
            new_rht = laplace(self.rht[old_key], t, s, corr)
            del self[old_key]
            self.add(new_lht, new_rht)

        # Carry out the transforms in all solutions.
        old_vars = self.solutions.keys()
        for old_var in old_vars:
            new_var = laplace(old_var, t, s, corr)
            new_sol = laplace(self.solutions[old_var], t, s, corr)
            del self.solutions[old_var]
            self.solutions[new_var] = new_sol

        if show:
            self.show()


def linearize(f, x=None, x_0=0, local_model=False):
    """Linearize a symbolic expression.

    Args
    ----
    f
        A nonlinear symbolic expression.
    x
        The variable to linearize for.
    x_0
        The linearization point.
    local_model : optional
        If True, return the local model Δy = mΔx

    Returns
    -------
    A symbolic expression.

    Employs: https://docs.sympy.org/latest/modules/series/series.html#more-intuitive-series-expansion
    """
    res = sp.series(f, x, x_0, n=2)
    res = res.removeO()  # Drop the remainder terms.
    if local_model:
        # Replace with the local difference variable.
        res = res.subs(x, x + x_0) - f.subs(x, x_0)
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


def laplace(expr, t, s, correspondence=None):
    """Calculate the Laplace transform of an expression.

    Args
    ----
    expr
        The expression.
    t : sp.Symbol
        The frequency-domain variable.
    s : sp.Symbol
        The time-domain variable
    correspondence : dict, optional
        A dictionary to assign time-domain function f to frequency-domain function F.
        Required when there are functions in expr.

    """
    # Calculate the inverse laplace transform.
    expr_s_ = sp.laplace_transform(expr, t, s, noconds=True)
    # Find the functions of t.
    funcs_t = find_functions(expr_s_, t)
    if len(funcs_t) > 0:
        # Replace them with a capital letter.
        expr_s_ = sp.laplace_correspondence(expr_s_, correspondence)
    # Set the initial conditions to 0.
    init_conds = {f: [0] * 5 for f in funcs_t}
    expr_s_ = sp.laplace_initial_conds(expr_s_, t, init_conds)

    return expr_s_


def build_correspondence(f_time, f_freq):
    """Build a correspondence dictionary between two iterables.

    Args
    ----
    f_time: Iterable
        The functions in the time domain.
    f_freq: Iterable
        The corresponding functions in the frequency domain.
    """

    return {t.func: f.func for t, f in zip(f_time, f_freq)}


def _upper(symbol):
    """Return a new symbol with the same name but the first letter is capital."""
    upper = copy(symbol)
    upper.name = upper.name.capitalize()
    return upper


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
