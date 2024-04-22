"""
=================================
Variable (:mod:`nodimo.variable`)
=================================

This module contains the classes to create a product of variables.

Classes
-------
BasicProduct
    Base class for the product of variables.
Product
    Creates a symbolic product of variables.
"""

from sympy import Mul, srepr

from nodimo.variable import BasicVariable
from nodimo.matrix import BasicDimensionalMatrix


# # Alias for type used in VariableGroup.
# ListOrMatrix = Union[list, Matrix]


class BasicProduct(BasicVariable):
    """Base class for the product of variables.

    Base class that represents the product of variables. The dimensional
    properties of the product are calculated from the input variables.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that compose the product.
    dependent : bool, default=False
        If ``True``, the product is dependent.
    scaling : bool, default=False
        If ``True``, the product can be used as scaling parameter.

    Attributes
    ----------
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the product is dependent.
    is_scaling : bool
        If ``True``, the product can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the product is nondimensional.

    Raises
    ------
    ValueError
        If the product is set as both dependent and scaling.
    ValueError
        If the product is set as scaling when it has no dimensions.
    """
    
    def __new__(
        cls,
        *variables: BasicVariable,
        dependent: bool = False,
        scaling: bool = False
    ):

        if len(variables) == 0:
            return BasicVariable()
        if len(variables) == 1:
            return variables[0]
        else:
            return super().__new__(cls)

    def __init__(
        self,
        *variables: BasicVariable,
        dependent: bool = False,
        scaling: bool = False
    ):

        super().__init__()
        self._variables: tuple[BasicVariable] = variables

        var1 = variables[0]
        var2 = BasicProduct(*variables[1:])
        self._set_dimensions(var1, var2)  # TODO: Check if i really need this class to work as a binary operator. Couldn't i evaluate the dimensions all at once?

        self.is_dependent = dependent
        self.is_scaling = scaling

    # Redefining dimensions as a read-only property
    @property
    def dimensions(self) -> dict[str, int]:
        return self._dimensions

    def _set_dimensions(self, var1, var2):
        """Evaluates the dimensions of the product of two variables."""

        if var1.is_nondimensional and var2.is_nondimensional:
            pass
        elif var1.is_nondimensional:
            self._dimensions = var2.dimensions
        elif var2.is_nondimensional:
            self._dimensions = var1.dimensions
        else:
            dimensional_matrix = BasicDimensionalMatrix(var1, var2)
            exponents = []
            for row in dimensional_matrix._raw_matrix:
                exponents.append(sum(row))
            
            self._dimensions = dict(zip(dimensional_matrix.dimensions, exponents))
            self._clear_null_dimensions()

        self._is_nondimensional = all(dim == 0 for dim in self._dimensions.values())


class Product(BasicProduct, Mul):
    """Creates a symbolic product of variables.

    This class inherits the dimensional properties of BasicProduct and
    adds to it, by inheriting from sympy.Mul, the ability to be used
    in symbolic mathematical expressions.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that compose the product.
    dependent : bool, default=False
        If ``True``, the product is dependent.
    scaling : bool, default=False
        If ``True``, the product can be used as scaling parameter.

    Attributes
    ----------
    dimensions : dict[str, int]
        Dictionary containing dimensions' names and exponents.
    is_dependent : bool
        If ``True``, the product is dependent.
    is_scaling : bool
        If ``True``, the product can be used as scaling parameter.
    is_nondimensional : bool
        If ``True``, the product is nondimensional.

    Raises
    ------
    ValueError
        If the product is set as both dependent and scaling.
    ValueError
        If the product is set as scaling when it has no dimensions.
    """
    
    def __new__(
        cls,
        *variables: BasicVariable,
        dependent: bool = False,
        scaling: bool = False
    ):

        return Mul.__new__(cls, *variables)

    def __init__(
        self,
        *variables: BasicVariable,
        dependent: bool = False,
        scaling: bool = False
    ):

        super().__init__(*variables, dependent=dependent, scaling=scaling)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = srepr(self._variables)[1:-1]
        dependent_repr = f', dependent=True' if self.is_dependent else ''
        scaling_repr = f', scaling=True' if self.is_scaling else ''

        return (f'{class_name}('
                + variables_repr
                + dependent_repr
                + scaling_repr
                + ')')

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy.
        
        This method is necessary to avoid the calling of
        LatexPrinter._print_Product, which corresponds to sympy.Product.
        """

        return printer._print_Mul(self)


Prod = Product


# class VariableProduct(BasicVariable, Mul):
#     """Creates a product of variables, each raised to an exponent.

#     A VariableProduct consists of a product of variables, each raised to
#     a particular exponent. The dimensional characteristics of this group
#     of variables are evaluated and stored as attributes.

#     Parameters
#     ----------
#     variables : list[Variable]
#         List of variables that constitute the group.
#     exponents : list or Matrix
#         List or matrix containing each variable's exponent.
#     check_inputs : bool, default=True
#         If ``True``, variables and exponents are validated.

#     Attributes
#     ----------
#     variables : list[Variable]
#         List of variables that constitute the group.
#     exponents : Matrix
#         Matrix containing each variable's exponent.
#     dimensions : dict[str, int]
#         Dictionary containing dimensions' names and exponents.
#     is_dependent : bool
#         If ``True``, the group is dependent.
#     is_nondimensional : bool
#         If ``True``, the group is nondimensional.

#     Raises
#     ------
#     TypeError
#         If the type of ``exponents`` is not ``list`` or ``Matrix``.
#     TypeError
#         If the list of variables contains at least one not-Variable.
#     ValueError
#         If the number of different variables is lower than two.
#     ValueError
#         If the numbers of variables and exponents do not match.
#     ValueError
#         If the exponents are not in a row matrix.
        
#     Examples
#     --------
#     Consider the dimensions mass ``M``, length ``L`` and time ``T``.
#     Next, assuming that ``V`` is velocity, ``D`` is characteristic
#     length, ``rho`` is density and ``mu`` is dynamic viscosity, the
#     Reynolds number ``Re`` is built as:

#     >>> from nodimo import Variable, VariableGroup
#     >>> rho = Variable('rho', M=1, L=-3)
#     >>> V = Variable('V', L=1, T=-1)
#     >>> D = Variable('D', L=1)
#     >>> mu = Variable('mu', M=1, L=-1, T=-1)
#     >>> Re = VariableGroup([rho, V, D, mu], [1, 1, 1, -1])
#     """

#     def __new__(cls,
#                 variables: list[BasicVariable],
#                 exponents: ListOrMatrix,
#                 dependent: bool = False,
#                 scaling: bool = False):

#         exponents = cls._convert_exponents(exponents)
#         cls._validate_variables_and_exponents(variables, exponents)

#         exponents_list = exponents.tolist()[0]
#         terms = [var**exp for var, exp in zip(variables, exponents_list)]

#         return super().__new__(cls, *terms)

#     def __init__(self,
#                  variables: list[BasicVariable],
#                  exponents: ListOrMatrix,
#                  dependent: bool = False,
#                  scaling: bool = False):

#         super().__init__()
#         self.variables: list[BasicVariable] = list(variables)
#         self.exponents: Matrix = self._convert_exponents(exponents)

#         # If all variables are nondimensional, there is no need to
#         # determine the dimensional properties.
#         self._is_nondimensional = all(var.is_nondimensional
#                                       for var in self.variables)
        
#         if self.is_nondimensional:
#             self.dimensions = dict()
#         else:
#             self._get_dimensions()
    
#         self.is_dependent = dependent
#         self.is_scaling = scaling        
    
#     @classmethod
#     def _convert_exponents(cls, exponents: ListOrMatrix) -> Matrix:
#         """Converts a container of type ``list`` to the type ``Matrix``.

#         Parameters
#         ----------
#         exponents : list or Matrix
#             A container with numbers.

#         Returns
#         -------
#         new_exponents: Matrix
#             The ``exponents`` container converted to ``Matrix`` type. If
#             the original container is already of the type ``Matrix``, no
#             conversion is done and ``new_exponents`` is equal to
#             ``exponents``.

#         Raises
#         ------
#         TypeError
#             If the type of ``exponents`` is not ``list`` or ``Matrix``.
#         """

#         if not isinstance(exponents, (list, Matrix)):
#             raise TypeError("exponents type must be list or sympy.Matrix")

#         if isinstance(exponents, list):
#             new_exponents = sp.Matrix([exponents])
#             new_exponents = sp.nsimplify(new_exponents,
#                                          rational=True).as_mutable()
#         else:
#             new_exponents = exponents

#         return new_exponents

#     @classmethod
#     def _validate_variables_and_exponents(cls,
#                                           variables: list[BasicVariable],
#                                           exponents: Matrix) -> None:
#         """Validates provided variables and exponents.

#         Parameters
#         ----------
#         variables: list[Variable]
#             List of variables that constitute the group.
#         exponents: Matrix
#             List or matrix containing each variable's exponent.

#         Raises
#         ------
#         TypeError
#             If the list of variables contains at least one not-Variable.
#         ValueError
#             If the number of different variables is lower than two.
#         ValueError
#             If the numbers of variables and exponents do not match.
#         ValueError
#             If the exponents are not in a row matrix.
#         """
        
#         if not all(isinstance(var, BasicVariable) for var in variables):
#             raise TypeError("All variables must be of type Variable")
#         elif len(set(variables)) < 2:
#             raise ValueError("Group must have at least two distinct variables")
#         elif len(variables) != sp.Mul(*exponents.shape):
#             raise ValueError("Number of variables and exponents must match")
#         elif exponents.shape[0] != 1:
#             raise ValueError("Exponents must be in a row matrix")

#     def _get_dimensions(self) -> None:
#         """Evaluates the dimensional properties of the group."""

#         # First, get dimensions names.
#         dimensions_names = _obtain_dimensions(*self.variables)

#         # Second, get dimensions exponents.
#         dimensional_matrix = _build_dimensional_matrix(self.variables,
#                                                        dimensions_names)

#         dimensions_exponents = dimensional_matrix * self.exponents.T

#         # Third, combine names and exponents.
#         self.dimensions = dict(zip(dimensions_names, dimensions_exponents))

#     def _set_dependent_from_variables(self) -> None:
#         """Set is_dependent property from component variables.

#         The group is dependent if it contains a dependent variable with
#         exponent.
#         """

#         is_dependent = [var.is_dependent for var in self.variables]
#         has_exponent = list(map(bool, self.exponents.tolist()[0]))
#         self.is_dependent = any(
#             [dep and exp for (dep,exp) in zip(is_dependent, has_exponent)]
#         )

#     def _sympyrepr(self, printer) -> str:
#         """String representation according to Sympy."""

#         class_name = type(self).__name__
#         variables_repr = f"[{', '.join(sp.srepr(var) for var in self.variables)}]"

#         exponents_repr_list = []
#         for e in self.exponents.tolist()[0]:
#             if e.is_Integer or e.is_Rational:
#                 exponents_repr_list.append(str(e))
#             else:
#                 exponents_repr_list.append(sp.srepr(e))

#         exponents_repr = f", [{', '.join(exponents_repr_list)}]"
#         dependent_repr = f', dependent=True' if self.is_dependent else ''
#         scaling_repr = f', scaling=True' if self.is_scaling else ''

#         return (f'{class_name}('
#                 + variables_repr
#                 + exponents_repr
#                 + dependent_repr
#                 + scaling_repr
#                 + ')')


# # Alias for VariableGroup.
# VarProduct = VariableProduct
