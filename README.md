<p align="center" width="100%">
    <img src="docs/logo/logo_name_side.svg" alt="Nodimo Logo" width="500">
</p>

---

| **Docs**    | [![Docs Status Badge]][Docs Status]                                           |
| :---------- | :---------------------------------------------------------------------------- |
| **Tests**   | [![Tests Status Badge]][Tests Status] [![Coverage Badge]][Coverage]           |
| **Python**  | [![Python Versions Badge]][Python Versions]                                   |
| **Version** | [![PyPI Version Badge]][PyPI Version] [![Conda Version Badge]][Conda Version] |
| **License** | [![License Badge]][License]                                                   |

# Nodimo
The main purpose of Nodimo is to transform a dimensional relationship between variables into a nondimensional one. The variables are gathered in nondimensional groups such that the number of groups is lower than the number of variables. The resulting nondimensional model is, at the same time, a generalization and simplification of the dimensional model.

Nodimo supports any number of dimensions and variables. It can be used for applications in science, engineering, economics and finance. The resulting nondimensional groups can be used as the basis for further studies in similarity and model testing.

## Installation
Nodimo and its dependencies (`numpy` and `sympy`) are installed by:
```shell
pip install nodimo
```

Alternatively, Nodimo and dependencies can be installed via `conda`:
```shell
conda install nodimo --channel rodrigopcastro018
```

When running Nodimo on the terminal, make sure that the terminal supports Unicode characters. For the best experience, it is recommended the use of [jupyter notebook][Jupyter Notebook].

## Getting started
### Basic example
* Simple pendulum

<p align="center" width="100%">
    <img width="30%" src="docs/tutorials/drawings/01_simple_pendulum.svg" alt="Simple Pendulum">
</p>

The nondimensional model for the pendulum's period `T` as a function of the other variables is built and displayed as:

```python
from nodimo import Variable, NonDimensionalModel

T = Variable('T', mass=0, length=0, time=1, dependent=True)  # period
L = Variable('L', mass=0, length=1, time=0, scaling=True)    # length
m = Variable('m', mass=1, length=0, time=0)                  # mass
g = Variable('g', mass=0, length=1, time=-2, scaling=True)   # gravity
t0 = Variable('theta_0')                                     # initial angle

ndmodel = NonDimensionalModel(T, L, m, g, t0)
ndmodel.show()
```

And the result is:

$$\displaystyle \frac{T g^{\frac{1}{2}}}{L^{\frac{1}{2}}} = \Pi{\left(\theta_{0} \right)}$$

For more applications and functionalities, check the [documentation][Docs Status].

# Aknowledgements

<!-- Links -->
[Docs Status]: https://nodimo.readthedocs.io/
[Docs Status Badge]: https://img.shields.io/readthedocs/nodimo?color=8A2BE2
[Tests Status]: https://github.com/rodrigopcastro018/nodimo/actions/workflows/test.yml
[Tests Status Badge]: https://github.com/rodrigopcastro018/nodimo/actions/workflows/full_test.yml/badge.svg?branch=main
[Coverage]: https://coverage-badge.samuelcolvin.workers.dev/redirect/rodrigopcastro018/nodimo
[Coverage Badge]: https://coverage-badge.samuelcolvin.workers.dev/rodrigopcastro018/nodimo.svg
[Python Versions]: https://pypi.org/project/nodimo
[Python Versions Badge]: https://img.shields.io/pypi/pyversions/nodimo
[PyPI Version]: https://pypi.org/project/nodimo/
[PyPI Version Badge]: https://img.shields.io/pypi/v/nodimo?label=PyPI&color=orange
[Conda Version]: https://anaconda.org/rodrigopcastro018/nodimo
[Conda Version Badge]: https://img.shields.io/conda/v/rodrigopcastro018/nodimo?label=Conda&color=green
[PyPI Downloads]: https://pypi.org/project/nodimo
[PyPI Downloads Badge]: https://img.shields.io/pypi/dm/nodimo?label=PyPI%20downloads&color=blue
[Conda Downloads]: https://anaconda.org/rodrigopcastro018/nodimo
[Conda Downloads Badge]: https://img.shields.io/conda/d/rodrigopcastro018/nodimo?label=Conda%20downloads&color=green
[License]: https://github.com/rodrigopcastro018/nodimo/blob/main/LICENSE
[License Badge]: https://img.shields.io/github/license/rodrigopcastro018/nodimo?label=License&color=yellow
[Jupyter Notebook]: https://github.com/jupyter/notebook
