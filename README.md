<p align="center" width="100%">
    <img src="https://github.com/rodrigopcastro018/nodimo/raw/main/docs/logo/logo_name_side.svg" alt="Nodimo Logo" width="500">
</p>

---

| **Docs**    | [![Docs Status Badge]][Docs Status]                                           |
| :---------- | :---------------------------------------------------------------------------- |
| **Tests**   | [![Tests Status Badge]][Tests Status] [![Coverage Badge]][Coverage]           |
| **Python**  | [![Python Versions Badge]][Python Versions]                                   |
| **Version** | [![PyPI Version Badge]][PyPI Version] [![Conda Version Badge]][Conda Version] |
| **License** | [![License Badge]][License]                                                   |

# Nodimo
The main purpose of Nodimo is to transform a dimensional relationship between quantities into a dimensionless one. This is done by grouping dimensional quantities into dimensionless products in such a way that the resulting number of products is always lower than or equal to the starting number of quantities. Therefore, the ensuing dimensionless model is, at the same time, a generalization and simplification of the dimensional model.

Nodimo supports any number of dimensions and quantities. It can be used for applications in science, engineering, economics and finance. The resulting dimensionless relations can be used as the basis for further studies in similarity and model testing.

## Notes

* The use of Nodimo requires basic knowledge of dimensional analysis, specially on choosing the appropriate set of scaling parameters and indentifying established dimensionless groups.

* It is recommended the use of [jupyter notebook][Jupyter Notebook] for a better displaying of the results.

## Installation
Via `PyPI`, Nodimo and its dependency `Sympy` is installed by:
```shell
pip install nodimo
```

Alternatively, via `Conda`:
```shell
conda install nodimo --channel rodrigopcastro018
```

## Getting started
### Basic example
* Simple pendulum

<p align="center" width="100%">
    <img width="30%" src="https://github.com/rodrigopcastro018/nodimo/raw/main/docs/tutorials/drawings/01_simple_pendulum.svg" alt="Simple Pendulum">
</p>

The dimensionless relation between the pendulum's period `T` and the other quantities presented in the figure above is built and displayed as:

```python
from nodimo import Quantity, Model

T = Quantity('T', mass=0, length=0, time=1, dependent=True)  # period
L = Quantity('L', mass=0, length=1, time=0, scaling=True)    # length
m = Quantity('m', mass=1, length=0, time=0)                  # mass
g = Quantity('g', mass=0, length=1, time=-2, scaling=True)   # gravity
t0 = Quantity('theta_0')                                     # initial angle

model = Model(T, L, m, g, t0)
model.show()
```

And the result is:

$$\displaystyle \frac{T g^{\frac{1}{2}}}{L^{\frac{1}{2}}} = \Phi{\left(\theta_{0} \right)}$$

For more applications and functionalities, check the [documentation][Docs Status].

<!-- Links -->
[Docs Status]: https://nodimo.readthedocs.io/
[Docs Status Badge]: https://img.shields.io/readthedocs/nodimo?color=8A2BE2
[Tests Status]: https://github.com/rodrigopcastro018/nodimo/actions/workflows/full_test.yml?query=branch%3Amain
[Tests Status Badge]: https://img.shields.io/github/actions/workflow/status/rodrigopcastro018/nodimo/full_test.yml?branch=main&label=Tests
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
[Jupyter Notebook]: https://jupyter.org/
