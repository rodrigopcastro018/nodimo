#         ┓•         Licensed under the MIT License
#    ┏┓┏┓┏┫┓┏┳┓┏┓    Copyright (c) 2024 Rodrigo Castro
#    ┛┗┗┛┗┻┗┛┗┗┗┛    https://nodimo.readthedocs.io

"""
Relation
========

This module contains the class to create a relation between quantities.

Classes
-------
Relation
    Creates a relation between quantities.
"""

from sympy import Symbol, Equality, Function
from sympy.printing.pretty.stringpict import prettyForm

from nodimo.quantity import Quantity, Constant
from nodimo.groups import HomogeneousGroup, IndependentGroup
from nodimo._internal import _prettify_name


class Relation(HomogeneousGroup, IndependentGroup):
    """Creates a relation between quantities.

    Parameters
    ----------
    *quantities : Quantity
        Quantities that constitute the relation.

    Attributes
    ----------
    quantities : list[Quantity]
        Quantities that constitute the relation.

    Raises
    ------
    ValueError
        If there is more than one dependent quantity.

    Examples
    --------

    >>> from nodimo import Quantity, Relation
    >>> F = Quantity('F', M=1, L=1, T=-2, dependent=True)
    >>> m = Quantity('m', M=1)
    >>> a = Quantity('a', L=1, T=-2)
    >>> rel = Relation(F, m, a)
    """

    def __init__(self, *quantities: Quantity, name: str = 'f'):
        super(Relation, self).__init__(*quantities)
        super(HomogeneousGroup, self).__init__(*self._quantities)
        self._name: str = name
        self._set_relation()

    def _set_relation(self):
        self._set_dependent_quantities()
        self._validate_relation()
        self._set_symbolic_relation()

    def _validate_relation(self):
        if len(self._dependent_quantities) > 1:
            raise ValueError("A relation cannot have more than one dependent quantity")
        elif len(self._dependent_quantities) == 0:
            self._dependent_quantities = (Constant('const'),)

    def _set_symbolic_relation(self):
        dep_qty = self._dependent_quantities[0]
        indep_qts_func = Function(self._name)(*self._independent_quantities)
        self._symbolic = Equality(dep_qty, indep_qts_func, evaluate=False)

    def _key(self) -> tuple:
        return (
            tuple(self._dependent_quantities),
            frozenset(self._independent_quantities),
        )

    def _sympy_(self):
        return self._symbolic

    def _sympyrepr(self, printer) -> str:
        class_name = type(self).__name__
        quantities = ', '.join(
            printer._print(qty._unreduced) for qty in self._quantities
        )
        name = f", name='{self._name}'" if self._name != 'f' else ''

        return f'{class_name}({quantities}{name})'

    def _sympystr(self, printer) -> str:
        name = self._name
        dep_qty = printer._print(self._dependent_quantities[0]._unreduced)
        indep_qts = ', '.join(
            printer._print(qty._unreduced) for qty in self._independent_quantities
        )

        return f'{dep_qty} = {name}({indep_qts})'

    def _latex(self, printer) -> str:
        name = printer._print(Symbol(self._name))
        dep_qty = printer._print(self._dependent_quantities[0]._unreduced)
        indep_qts = R',\ '.join(
            printer._print(qty._unreduced) for qty in self._independent_quantities
        )

        return f'{dep_qty} = {name}\\left({indep_qts}\\right)'

    def _pretty(self, printer) -> prettyForm:
        name = _prettify_name(self._name)
        dep_qty = printer._print(self._dependent_quantities[0]._unreduced)
        indep_qts = prettyForm('')
        for i, qty in enumerate(self._independent_quantities):
            sep = ', ' if i > 0 else ''
            indep_qts = prettyForm(
                *indep_qts.right(sep, printer._print(qty._unreduced))
            )
        indep_qts = prettyForm(*indep_qts.parens())

        return prettyForm(*dep_qty.right(' = ', name, indep_qts))
