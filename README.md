# penbegone

Take your math from the paper to the screen.

`penbegone` is a small library of [SymPy](https://www.sympy.org) helpers for control-systems math in Jupyter notebooks.

## Features

- `Equations`: a numbered system of equations that you solve one step at a time.
- `laplace` and `ilaplace`: the Laplace transform and its inverse, with support for functions such as `f(t)`.
- `linearize`: linearization of one or more expressions about a point.
- `series`, `parallel` and `feedback`: combinations of transfer functions.
- `final_value_time` and `final_value_freq`: final values in the time domain and the frequency domain.
- `plotting.pole_zero`: the pole-zero plot of a system.

## Installation

The project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

The examples use these imports:

```python
import sympy as sp

from penbegone import plotting
from penbegone.common import *
```

### The `Equations` class

`Equations` holds a numbered system of equations. You solve the system one step at a time, as on paper.

| Method                | What it does                                                                       |
| --------------------- | ---------------------------------------------------------------------------------- |
| `add(left, right)`    | Adds an equation and gives it the next number.                                     |
| `rearrange(key, var)` | Solves one equation for a variable.                                                |
| `use_eq(key, var)`    | Solves one equation for a variable, then substitutes the result in all the others. |
| `apply(var, expr)`    | Substitutes a known value in the full system.                                      |
| `subs(dict)`          | Does a plain SymPy substitution in the full system.                                |
| `solve(variables)`    | Solves the full system automatically.                                              |
| `laplace(t, s, corr)` | Transforms the full system to the frequency domain.                                |
| `show()`              | Prints the new equations and solutions in the notebook.                            |

```python
x1, x2 = sp.symbols("x_1 x_2")
eqs = Equations()
eqs.add(x1, 2 * x2)  # [1]: x_1 = 2 x_2
eqs.add(x2, x1 + 1)  # [2]: x_2 = x_1 + 1

eqs.use_eq(1, x1)  # Solutions: {x_1: 2*x_2}. New equation [3]: x_2 = 2*x_2 + 1
eqs.use_eq(3, x2)  # Solutions: {x_1: -2, x_2: -1}. No equations stay.
```

`eqs.solve()` gives the same result in one step: `{x_1: -2, x_2: -1}`.

### The Laplace transform

| Function                                | What it does                                                      |
| --------------------------------------- | ----------------------------------------------------------------- |
| `functions("y u", t)`                   | Makes the functions `y(t)` and `u(t)`.                            |
| `build_correspondence(f_time, f_freq)`  | Connects `y(t)` to `Y(s)`.                                        |
| `laplace(expr, t, s, corr, init_conds)` | Transforms an expression. The default is zero initial conditions. |
| `ilaplace(expr, s, t)`                  | Does the inverse transform.                                       |

A first-order system, from the differential equation to the transfer function:

```python
s, t, a, K, tau = sp.symbols("s t a K tau")
y, u = functions("y u", t)
Y, U = functions("Y U", s)
corr = build_correspondence([y, u], [Y, U])

eqs = Equations()
eqs.add(tau * y.diff(t) + y, K * u)
eqs.laplace(t, s, corr)  # [2]: s*tau*Y(s) + Y(s) = K*U(s)
eqs.solve([Y])  # {Y(s): K*U(s)/(s*tau + 1)}
```

Single expressions:

```python
laplace(sp.exp(-a * t), t, s)  # 1/(a + s)
laplace(y.diff(t, 2), t, s, corr, {y.func: [1, 0]})  # s**2*Y(s) - s
ilaplace(1 / (s + a), s, t)  # exp(-a*t)*Heaviside(t)
```

### Linearization

`linearize(f, x, x_0, local_model=False)` accepts one expression or a list, and one variable or a list.
With `local_model=True`, it returns the local model Δy = mΔx.

```python
x, y, c = sp.symbols("x y c")
linearize(x**2, x, 2)  # 4*x - 4
linearize(c * sp.ln(x), x, 2, local_model=True)  # c*x/2
linearize([x**2 + y**2, x * y], [x, y], [1, 1])  # [2*x + 2*y - 2, x + y - 1]
linearize([x**2 + y**2, x * y], [x, y], [1, 1], local_model=True)  # [2*x + 2*y, x + y]
```

### Block diagrams

`tf`, `series`, `parallel` and `feedback` accept SymPy `TransferFunction` objects or plain expressions.

```python
G = tf(1, s, s)
H = tf(1, s + 1, s)
series(G, H)  # TransferFunction(1, s*(s + 1), s)
parallel(G, H)  # TransferFunction(2*s + 1, s*(s + 1), s)
feedback(G)  # TransferFunction(1, s + 1, s), unit negative feedback
feedback(K / s)  # K/(K + s), with plain expressions
```

### Analysis and display

| Function                     | Example input                         | Result                                   |
| ---------------------------- | ------------------------------------- | ---------------------------------------- |
| `final_value_time(expr, t)`  | `1 - 1.6*exp(-10*t) + 0.6*exp(-20*t)` | `1`                                      |
| `final_value_freq(expr, s)`  | `K / (s*(tau*s + 1))`                 | `K`                                      |
| `collect_powers(expr, s)`    | `(K*s + a*s + 1) / ((s + 1)*(s + a))` | `(s*(K + a) + 1)/(a + s**2 + s*(a + 1))` |
| `plotting.pole_zero(sys, s)` | `(s + 2) / (s**2 + 2*s + 5)`          | A pole-zero plot                         |
| `printeq(lhs, rhs)`          | `printeq(x, sp.pi * y)`               | `x = 3.14 y`                             |

`DISPLAY_PRECISION = 3` sets the number of digits in all printed output.

## Development

To change the code, read [DEVELOPERS.md](DEVELOPERS.md).
