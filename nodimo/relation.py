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

import sympy as sp
from sympy import sstr, Equality

from nodimo.variable import BasicVariable
from nodimo.group import PrintableGroup
from nodimo.specialgroups import HomogeneousGroup
from nodimo._internal import _repr


class BasicRelation(HomogeneousGroup):
    """Base class for a relation of variables.

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
    
    def __init__(self, *variables: BasicVariable, name: str = 'f'):

        super().__init__(*variables)
        self.name: str = name
        self._dependent_variable: BasicVariable
        self._independent_variables: tuple[BasicVariable]
        self._set_basicrelation_properties()

    def _set_basicrelation_properties(self):
        """Sets basic relation properties"""

        self._validate_variables()
        self._separate_dependent_variable()

    def _validate_variables(self):
        """Validates the existence of only one dependent variable.

        If no dependent variable is found, this method tries to define
        the first given variable as dependent.
        """

        is_dependent = [var.is_dependent for var in self._variables]
        if sum(is_dependent) == 0:
            try:
                self._variables[0].is_dependent = True
            except ValueError:
                raise ValueError("There must be exactly one dependent variable")
        elif sum(is_dependent) > 1:
            raise ValueError("There must be exactly one dependent variable")

    def _separate_dependent_variable(self):
        """Separates variables into dependent and independent."""
        
        independent_variables = []
        for var in self.variables:
            if var.is_dependent:
                dependent_variable = var
            else:
                independent_variables.append(var)

        self._dependent_variable = dependent_variable
        self._independent_variables = tuple(independent_variables)

    def __str__(self) -> str:

        dep_var_str = str(self._dependent_variable)
        indep_var_str = sstr(self._independent_variables)[1:-1]

        return dep_var_str + f' = {self.name}({indep_var_str})'

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variables_repr = _repr(self._variables)[1:-1]
        name_repr = f", name='{self.name}'" if self.name != 'f' else ''

        return f'{class_name}({variables_repr}{name_repr})'


class Relation(BasicRelation, PrintableGroup):
    """Creates a relation of variables.

    Similar to a BasicRelation, but with a functional relation as
    the representation in symbolic format.

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

    def __init__(self, *variables: BasicVariable, name: str = 'f'):

        super().__init__(*variables, name=name)
        self._set_relation_properties()

    def _set_relation_properties(self):
        """Sets basic relation properties"""

        self._build_functional_relation()

    def _build_functional_relation(self):
        """Builds functional relation between variables."""

        dep_var = self._dependent_variable
        indep_vars_func = sp.Function(self.name)(*self._independent_variables)
        self._function = Equality(dep_var, indep_vars_func, evaluate=False)

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return printer._print_Relational(self._function)

    def _sympyrepr(self, printer) -> str:
        """String representation according to Sympy."""

        return BasicRelation.__repr__(self)

    _latex = _pretty = _sympystr
