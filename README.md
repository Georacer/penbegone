# penbegone

[![Release](https://img.shields.io/github/v/release/Georacer/penbegone)](https://img.shields.io/github/v/release/Georacer/penbegone)
[![Build status](https://img.shields.io/github/actions/workflow/status/Georacer/penbegone/main.yml?branch=main)](https://github.com/Georacer/penbegone/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/Georacer/penbegone/branch/main/graph/badge.svg)](https://codecov.io/gh/Georacer/penbegone)
[![Commit activity](https://img.shields.io/github/commit-activity/m/Georacer/penbegone)](https://img.shields.io/github/commit-activity/m/Georacer/penbegone)
[![License](https://img.shields.io/github/license/Georacer/penbegone)](https://img.shields.io/github/license/Georacer/penbegone)

Take your math from the paper to the screen

- **Github repository**: <https://github.com/Georacer/penbegone/>
- **Documentation** <https://Georacer.github.io/penbegone/> and <https://fpgmaas.github.io/cookiecutter-poetry/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:Georacer/penbegone.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPi or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

## Releasing a new version

- Create an API Token on [Pypi](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/Georacer/penbegone/settings/secrets/actions/new).
- Create a [new release](https://github.com/Georacer/penbegone/releases/new) on Github.
- Create a new tag in the form `*.*.*`.

For more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/cicd/#how-to-trigger-a-release).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
