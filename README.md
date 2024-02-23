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
In the following example, we ...
```python
from nodimo import Variable, NonDimensionalModel
```


```python
T = Variable('T', M=0, L=0, T=1, dependent=True)
L = Variable('L', M=0, L=1, T=0, scaling=True)
m = Variable('m', M=1, L=0, T=0)
g = Variable('g', M=0, L=1, T=-2, scaling=True)
t0 = Variable('theta_0')

ndmodel = NonDimensionalModel(T, L, m, g, t0)
```

Nodimo detects that the mass and its dimension can not belong to the model
```
Variables that can not be part of the model:
    m
Dimensions that can not be part of the model:
    M
```

```python
ndmodel.dimensional_function.show()
```
$\displaystyle T = \pi{\left(L,g,\theta_{0} \right)}$

```python
ndmodel.dimensional_matrix.show()
```
$\displaystyle \begin{array}{r|rrrr} & T & L & g & \theta_{0}\\ \hline \mathtt{\text{L}} & \phantom{-}0 & \phantom{-}1 \phantom{-}1 & \phantom{-}0\\ \mathtt{\text{T}} & \phantom{-}1 & \phantom{-}0 & -2 & \phantom{-}0\\ \end{array}$

```python
ndmodel.show()
```
$\displaystyle \frac{T g^{\frac{1}{2}}}{L^{\frac{1}{2}}} = \Pi{\left(\theta_{0} \right)}$

## License
Nodimo is open-source and released under the [MIT License](LICENSE)