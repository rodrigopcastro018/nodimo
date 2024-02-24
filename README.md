# Nodimo

The main purpose of Nodimo is to transform a dimensional relationship
between variables into a nondimensional one. The variables are gathered
in nondimensional groups such that the number of groups is lower than
the number of variables. The resulting nondimensional model is, at the
same time, a generalization and simplification of the dimensional model.

Nodimo supports any number of dimensions and variables. It can be used
for applications in science, engineering, economics, finance, medicine
and pharmacology. The resulting nondimensional groups can be used as the
basis for further studies in similarity and model testing.

## Installation

### Prerequisites
Nodimo requires `numpy` and `sympy`, which are automatically installed.

### Install Nodimo
```shell
pip install nodimo
```

## Getting started
### Basic example
This example deals with the simple pendulum problem (see image below).

![Simple Pendulum](https://github.com/rodrigopcastro018/nodimo/blob/main/example/simple_pendulum.png)

The nondimensional model for the pendulum's period as a function of the other
variables is built as:
```python
from nodimo import Variable, NonDimensionalModel

T = Variable('T', M=0, L=0, T=1, dependent=True)
L = Variable('L', M=0, L=1, T=0, scaling=True)
m = Variable('m', M=1, L=0, T=0)
g = Variable('g', M=0, L=1, T=-2, scaling=True)
t0 = Variable('theta_0')

ndmodel = NonDimensionalModel(T, L, m, g, t0)
```

After that, the nondimensional model can be displayed with the following command
```python
ndmodel.show()
```
[comment]: <> ($\displaystyle \frac{T g^{\frac{1}{2}}}{L^{\frac{1}{2}}} = \Pi{\left(\theta_{0} \right)}$)
```math
\displaystyle \frac{T g^{\frac{1}{2}}}{L^{\frac{1}{2}}} = \Pi{\left(\theta_{0} \right)}
```

For more functionalities and examples, check the documentation.

## License
Nodimo is open-source and released under the [MIT License](LICENSE)