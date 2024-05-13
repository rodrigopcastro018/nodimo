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

from sympy import sstr, srepr, Equality, Function

from nodimo.variable import Variable
from nodimo.groups import PrintableGroup, HomogeneousGroup


class Relation(PrintableGroup, HomogeneousGroup):
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

        HomogeneousGroup.__init__(self, *variables)
        self._name: str = name
        self._set_relation_properties()
        self._set_printgroup_properties()

    def _set_relation_properties(self):
        """Sets basic relation properties"""

        self._set_dependent_variables()
        self._validate_relation_variables()

    def _validate_relation_variables(self):
        if len(self._dependent_variables) != 1:
            raise ValueError("There must be exactly one dependent variable")

    def _build_symbolic(self):
        dep_var = self._dependent_variables[0]
        indep_vars_func = Function(self._name)(*self._independent_variables)
        self._symbolic = Equality(dep_var, indep_vars_func, evaluate=False)

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        variables_repr = ', '.join(srepr(var) for var in self._variables)
        name_repr = f", name='{self._name}'" if self._name != 'f' else ''

        return f'{class_name}({variables_repr}{name_repr})'

    # def _printmethod(self, printer):
    
    #     dep_var_str = str(self._dependent_variable)
    #     indep_var_str = ', '.join(sstr(var) for var in self._independent_variables)
    
    #     return dep_var_str + f' = {self._name}({indep_var_str})'
