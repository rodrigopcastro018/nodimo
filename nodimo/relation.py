"""
=======================================
Model Function (:mod:`nodimo.function`)
=======================================

This module contains the class to creates model functions.

Classes
-------
ModelFunction
    Creates a function that relates a set of variables or groups.
"""

from sympy import Equality, Function

from nodimo.variable import Variable
from nodimo.groups import HomogeneousGroup


class Relation(HomogeneousGroup):
    """Creates a relation of variables.

    This class builds a mathematical relation between one dependent
    variable and none or multiple independent variables.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that constitute the relation.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        Tuple with the variables.
    dimensions : tuple[str]
        Tuple with the dimensions' names.

    Raises
    ------
    ValueError
        If there is not exactly one dependent variable.
    """

    def __init__(self, *variables: Variable, name: str = 'f'):

        super().__init__(*variables)
        self._name: str = name
        self._set_relation()

    def _set_relation(self):
        self._set_dependent_variables()
        self._validate_relation()
        self._set_symbolic_relation()

    def _validate_relation(self):
        if len(self._dependent_variables) != 1:
            raise ValueError("There must be exactly one dependent variable")

    def _set_symbolic_relation(self):
        dep_var = self._dependent_variables[0]
        indep_vars_func = Function(self._name)(*self._independent_variables)
        self._symbolic = Equality(dep_var, indep_vars_func, evaluate=False)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variables = ', '.join(printer._print(var) for var in self._variables)
        name = f", name='{self._name}'" if self._name != 'f' else ''

        return f'{class_name}({variables}{name})'

    def _sympystr(self, printer) -> str:
        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.

        dep_var = printer._print(self._dependent_variables[0])
        indep_vars = ', '.join(
            printer._print(var) for var in self._independent_variables
        )

        return f'{dep_var} = {self._name}({indep_vars})'

    def _latex(self, printer):
        return printer._print(self._symbolic)
    
    _pretty = _latex
