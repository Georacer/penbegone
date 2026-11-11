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

## Example

```python
import sympy as sp

import penbegone as pbg

x1, x2 = sp.symbols("x_1, x_2")
eqs = pbg.common.Equations()
eqs.add(x1, 2 * x2)
eqs.add(x2, x1 + 1)
eqs.use_eq(1, x1)  # Solve equation 1 for x1 and substitute the result.
eqs.show()
```

## Development

| Task                           | Command                                  |
| ------------------------------ | ---------------------------------------- |
| Install the pre-commit hooks   | `uv run pre-commit install`              |
| Run the tests                  | `uv run pytest`                          |
| Run the tests with coverage    | `uv run pytest --cov`                    |
| Run ruff and the other hooks   | `uv run pre-commit run -a`               |
| Run the type checker           | `uv run mypy`                            |
| Test on another Python version | `uv run --isolated --python 3.10 pytest` |
