"""
=============================
Models (:mod:`nodimo.models`)
=============================

This module contains the classes to create (non)dimensional models.

Classes
-------
DimensionalModel
    Creates a dimensional model from a given set of variables.
NonDimensionalModel
    Creates nondimensional models from a given set of variables.
"""

from itertools import combinations

from nodimo.variable import Variable
from nodimo.groups import NonDimensionalGroup, ScalingGroup
from nodimo.relation import Relation
from nodimo._internal import _print_horizontal_line


class Model(Relation):
    """Creates (non)dimensional relations from a given set of variables.

    This model builds relations using the resulting variables of a group
    transformation.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the model.

    Attributes
    ----------
    relations : dict[ScalingGroup, Relation]
        Dictionary containing pairs of scaling groups and relations.

    Methods
    -------
    show()
        Displays scaling groups and respective (non)dimensional relations.

    Raises
    ------
    ValueError
        If the number of scaling variables is lower than necessary.

    Examples
    --------
    * Free fall

        Dimensions
        ``M``: mass
        ``L``: length
        ``T``: time

        Variables
        ``z``: height
        ``m``: mass
        ``v``: velocity
        ``g``: gravitational acceleration
        ``t``: time
        ``z0``: initial height
        ``v0``: initial velocity
    
    Considering the scaling groups that can be formed with ``g``, ``z0``
    and ``v0``, the ``model`` for ``z`` is built and displayed as:

    >>> from nodimo import Variable, Model
    >>> z = Variable('z', L=1, dependent=True)
    >>> m = Variable('m', M=1)
    >>> v = Variable('v', L=1, T=-1)
    >>> g = Variable('g', L=1, T=-2, scaling=True)
    >>> t = Variable('t', T=1)
    >>> z0 = Variable('z0', L=1, scaling=True)
    >>> v0 = Variable('v0', L=1, T=-1, scaling=True)
    >>> model = Model(z, m, v, g, t, z0, v0)
    >>> model.show()
    """

    def __init__(self, *variables: Variable):
        super().__init__(*variables)
        self._scaling_groups: tuple[ScalingGroup]
        self._relations: dict[ScalingGroup, Relation]
        self._set_model()

    @property
    def relations(self) -> dict[ScalingGroup, Relation]:
        return self._relations

    def _set_model(self):
        self._set_matrix_rank()
        self._set_scaling_variables()
        self._validate_model()
        self._set_scaling_groups()
        self._set_relations()

    def _validate_model(self):
        if len(self._scaling_variables) < self._rank:
            raise ValueError(
                f"The model must have at least {self._rank} scaling variables"
            )

    def _set_scaling_groups(self):
        scaling_groups = []
        for scgroup in combinations(self._scaling_variables, self._rank):
            try:
                scaling_groups.append(ScalingGroup(*scgroup))
            except:
                pass

        if len(scaling_groups) > 1:
            idnum = 1
            for scgroup in scaling_groups:
                scgroup._id_number = idnum
                idnum += 1

        self._scaling_groups = tuple(scaling_groups)
    
    def _set_relations(self):
        relations = {}
        for scgroup in self._scaling_groups:
            variables = list(self._nonscaling_variables)
            for var in self._scaling_variables:
                if var not in scgroup:
                    reset_var = var._copy()
                    reset_var.is_scaling = False
                    variables.append(reset_var)
            variables.extend(scgroup._variables)

            ndgroup = NonDimensionalGroup(*variables)
            for prod in ndgroup._products:
                prod.is_dependent = any(var.is_dependent for var in prod._variables)

            if scgroup._id_number is None:
                relation_name = 'Phi'
            else:
                relation_name = f'Phi_{scgroup._id_number}'

            relations[scgroup] = Relation(*ndgroup.variables, name=relation_name)

        self._relations = relations

    def show(self):
        super().show()
        for i, (scgroup, relation) in enumerate(self._relations.items()):
            _print_horizontal_line()
            scgroup.show(use_custom_css=False)
            relation.show()
