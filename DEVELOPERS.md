# Developer guide

This file tells you how to change the code of `penbegone`. To use the library, read [README.md](README.md).

## Setup

The project uses [uv](https://docs.astral.sh/uv/).

1. Install the environment: `uv sync`
2. Install the pre-commit hooks: `uv run pre-commit install`

The file `.python-version` pins the development environment to Python 3.15. The library supports Python 3.10 and later.

## Commands

| Task                                    | Command                                             |
| --------------------------------------- | --------------------------------------------------- |
| Run all tests                           | `uv run pytest`                                     |
| Run one test                            | `uv run pytest tests/test_generic.py::test_laplace` |
| Run all tests with coverage             | `uv run pytest --cov`                               |
| Run the tests on another Python version | `uv run --isolated --python 3.10 pytest`            |
| Run ruff and the other pre-commit hooks | `uv run pre-commit run -a`                          |
| Run the type checker                    | `uv run mypy`                                       |

Ruff uses a line length of 120 and runs with `fix = true`, so the pre-commit hook changes files.

## Architecture

All library code is in two modules. `penbegone/__init__.py` exports them as `penbegone.common` and `penbegone.plotting`. The tests import the package as `pbg`.

### `penbegone/common.py`

- **`Equations`** is the central class. It holds a numbered system of equations that the user solves by hand, one step at a time.
  - Three dictionaries share the same integer keys: `lht` and `rht` hold the two sides for display, and `eqs` holds `-left + right` for solving. Change all three together.
  - `_counter` gives each new equation the next key. When an equation changes, the class deletes it and adds it again with a new key. The class never uses a key again. The tests assert on these key values.
  - `use_eq(key, variable)` solves one equation for a variable, moves the result into `solutions`, deletes the equation, and substitutes the result into all other equations and solutions.
  - `show()` prints only the equations and solutions that are new since the last call. `_last_shown` and `solutions_updated` hold that state.
  - `apply()` uses the reserved key `"temp"` for a temporary equation.
- **Laplace helpers**: `laplace()` wraps `sp.laplace_transform`, then replaces time functions with frequency functions through a correspondence dictionary (`build_correspondence`), then applies initial conditions. The default is zero initial conditions (`build_initial_conditions`). `Equations.laplace()` applies this to the full system.
- **`linearize()`** dispatches on its input. A list of expressions recurses. One variable uses `sp.series`. A list of variables uses partial derivatives. `local_model=True` returns the local model Δy = mΔx.
- **`series()`, `parallel()`, `feedback()`** accept `sympy.physics.control.lti` objects or plain SymPy expressions. They examine the type of the first argument to select the method.
- **`functions()` and `find_functions()`** create and find applied undefined functions such as `f(t)`.
- **`DISPLAY_PRECISION`** is a module constant. It sets the `evalf` precision for all printed output.

Output goes through `IPython.display`, so the display functions are for a notebook.

### `penbegone/plotting.py`

`pole_zero()` wraps the SymPy pole-zero plot. It accepts a `TransferFunction` or a plain expression plus the variable `s`.

## Conventions

- Variable names in `common.py` and in the tests use a suffix convention: `A` is a SymPy symbol, `A_` is an expression, and `A__` is an evaluated expression.
- The tests compare expressions with `a - b == 0`, not with `a == b`.
- The source uses both NumPy-style (`Args` with a dashed underline) and Google-style docstrings.

## Dependencies

| Task                          | Command                               |
| ----------------------------- | ------------------------------------- |
| Add a library dependency      | `uv add <package>`                    |
| Add a development dependency  | `uv add --group dev <package>`        |
| Remove a dependency           | `uv remove <package>`                 |
| Upgrade one locked package    | `uv lock --upgrade-package <package>` |
| Make sure the lock is current | `uv lock --check`                     |

- Commit `uv.lock` together with each change to `pyproject.toml`.
- `matplotlib` is a dependency, but no module imports it directly. The SymPy pole-zero plot needs it.
- Ruff has two version entries: the `rev` in `.pre-commit-config.yaml` and the `dev` group in `pyproject.toml`. Keep them the same.

## CI

`.github/workflows/main.yml` starts on each push to `master` and on each pull request. It has two jobs:

- **`quality`** runs `uv lock --check`, `uv run pre-commit run -a` and `uv run mypy` on Python 3.15.
- **`test`** runs `uv run pytest --cov` on Python 3.10, 3.11, 3.12, 3.13, 3.14 and 3.15.

The two jobs use the composite action in `.github/actions/setup-uv-env` to install uv and the locked dependencies.

## Known problems

- The mypy configuration sets `disallow_untyped_defs`, but the source has no type annotations. `uv run mypy` reports 45 errors, and the `quality` job fails for the same reason.
