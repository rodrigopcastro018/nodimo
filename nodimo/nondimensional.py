"""
====================================================
Nondimensional Models (:mod:`nodimo.nondimensional`)
====================================================

This module contains the classes to create nondimensional models.

Classes
-------
NonDimensionalModel
    Creates a nondimensional model from a given set of variables.
NonDimensionalModels
    Creates nondimensional models from a given set of variables.
"""

import sympy as sp
from sympy import Matrix
from itertools import combinations

from nodimo.variable import BasicVariable, VariableProduct
from nodimo.relation import VariableRelation
from nodimo.dimensional import DimensionalModel
from nodimo._internal import (_is_running_on_jupyter,
                              _show_object,
                              _print_horizontal_line,
                              _build_dimensional_matrix)

if _is_running_on_jupyter:
    from IPython.display import Math


class NonDimensionalModel(DimensionalModel):
    """Creates a nondimensional model from a given set of variables.

    This class extends the dimensional model by introducing
    nondimensional groups and the nondimensional function, which
    describes the relationship between the groups and represents the
    model.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the model.
    build_now : bool, default=True
        If ``True``, the variables are validated and the model is built.
    display_messages : bool, default=True
        If ``True``, extra variables and dimensions are displayed.

    Attributes
    ----------
    nondimensional_groups : list[VariableGroup]
        List of nondimensional groups.
    nondimensional_function : ModelFunction
        Function that represents the nondimensional model.

    Methods
    -------
    build_nondimensional_model() = build()
        Builds the main characteristics of the nondimensional model.
    show_dimensional_model()
        Displays the dimensional model.
    show_nondimensional_model() = show()
        Displays the nondimensional model.

    Raises
    ------
    ValueError
        If the number of scaling variables is not adequate.
    ValueError
        If the scaling variables do not form an independent set.

    Examples
    --------
    * Simple Pendulum

    Consider the dimensions mass ``M``, length ``L`` and time ``T``.
    Next, assume that ``P`` is period, ``m`` is mass and, ``g`` is
    gravitational acceleration, ``R`` is the pendulum's length and
    ``t0`` is the initial angle. In addition, take ``g`` and ``D`` as
    the scaling parameters. The nondimensional model ``ndmodel`` for the
    period is built and displayed as:

    >>> from nodimo import Variable, NonDimensionalModel
    >>> P = Variable('P', T=1, dependent=True)
    >>> m = Variable('m', M=1)
    >>> g = Variable('g', L=1, T=-2, scaling=True)
    >>> R = Variable('R', L=1, scaling=True)
    >>> t0 = Variable('theta_0')
    >>> ndmodel = NonDimensionalModel(P, m, g, R, t0)
    >>> ndmodel.show()
    """

    def __init__(self,
                 *variables: BasicVariable,
                 build_now: bool = True,
                 display_messages: bool = True):

        super().__init__(*variables, display_messages=display_messages)

        # This attribute is used by the class NonDimensionalModels to
        # avoid the validation of the scaling variables.
        self._check_scaling_variables: bool = True

        self.nondimensional_groups: list[VariableProduct]
        self.nondimensional_function: VariableRelation

        if build_now:
            self._validate_scaling_variables()
            self.build_nondimensional_model()

    def _validate_scaling_variables(self) -> None:
        """Validates the set of scaling variables.

        Raises
        ------
        ValueError
            If the number of scaling variables is not adequate.
        ValueError
            If the scaling variables do not form an independent set.
        """

        if len(self.scaling_variables) != self.dimensional_matrix.rank:
            raise ValueError(f"The model must have "
                             f"{self.dimensional_matrix.rank} "
                             f"scaling variables.")

        A = _build_dimensional_matrix(self.scaling_variables, self.dimensions)

        if A.rank() != self.dimensional_matrix.rank:
            raise ValueError(
                "Scaling variables do not form an independent set")

    def build_nondimensional_model(self) -> None:
        """Builds the main properties of the nondimensional model."""

        if self._check_scaling_variables:
            self._validate_scaling_variables()

        self.nondimensional_groups = self._build_nondimensional_groups()

        self.nondimensional_function = VariableRelation(
            *self.nondimensional_variables,
            *self.nondimensional_groups,
            name='Pi'
        )

    # Alias for build_nondimensional_model.
    build = build_nondimensional_model

    def _build_exponents_matrix(self) -> Matrix:
        """Builds the matrix of exponents for the nondimensional groups.

        Returns
        -------
        exponents_matrix : Matrix
            Matrix containing the exponents, where each row is the
            corresponding dimensional variable, and every column
            represents a group.
        
        References
        ----------
        .. [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
               (Butterworth-Heinemann, 2007), p. 133.
        """

        number_of_dimensions = len(self.dimensions)
        number_of_variables = len(self.dimensional_variables)

        A = _build_dimensional_matrix(self.scaling_variables,
                                      self.dimensions)
        B = _build_dimensional_matrix(self.nonscaling_variables,
                                      self.dimensions)

        # In case the dimensional matrix has linear dependent rows.
        if number_of_dimensions > self.dimensional_matrix.rank:
            dimensional_matrix = B.row_join(A)
            _, independent_rows = dimensional_matrix.T.rref()
            A, B = A[independent_rows, :], B[independent_rows, :]

        # Components to build the matrix of exponents.
        E11 = sp.eye(number_of_variables - self.dimensional_matrix.rank)
        E12 = sp.zeros(number_of_variables - self.dimensional_matrix.rank,
                       self.dimensional_matrix.rank)
        E21 = -A**-1 * B
        E22 = A**-1

        E = sp.Matrix([[E11, E12],
                       [E21, E22]])

        Z1 = sp.eye(number_of_variables - self.dimensional_matrix.rank)
        Z2 = sp.zeros(self.dimensional_matrix.rank,
                      number_of_variables - self.dimensional_matrix.rank)

        Z = sp.Matrix([[Z1],
                       [Z2]])

        exponents_matrix = E * Z

        return exponents_matrix

    def _build_nondimensional_groups(self) -> list[VariableProduct]:
        """Builds nondimensional groups.

        Returns
        -------
        nondimensional_groups : list[VariableGroup]
            List containing the nondimensional groups.
        """

        exponents_matrix = self._build_exponents_matrix()

        nondimensional_groups = []

        for j in range(len(self.nonscaling_variables)):
            group = VariableProduct(self.dimensional_variables,
                                  exponents_matrix.col(j).T)
            group._set_dependent_from_variables()
            nondimensional_groups.append(group)

        return nondimensional_groups

    # Alias for the show method.
    show_nondimensional_model = DimensionalModel.show

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return sp.sstr(self.nondimensional_function)

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return sp.latex(self.nondimensional_function)


# Alias for the class NonDimensinalModel.
NonDimModel = NonDimensionalModel


class NonDimensionalModels(DimensionalModel):
    """Creates nondimensional models from a given set of variables.

    This class also extends the dimensional model, but its purpose is to
    gather multiple nondimensional functions built from distinct groups
    of scaling variables. It can be understood as a collection of
    nondimensional models.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the model.
    display_messages : bool, default=True
        If ``True``, extra variables and dimensions are displayed.

    Attributes
    ----------
    scaling_groups : list[list[Variable]]
        List containing sets of validated scaling groups.
    nondimensional_functions : list[ModelFunction]
        List with one nondimensional function for each scaling group.

    Methods
    -------
    show_dimensional_model()
        Displays the dimensional model.
    show_nondimensional_models() = show()
        Displays scaling groups and respective nondimensional models.

    Raises
    ------
    ValueError
        If the number of scaling variables is lower than necessary.

    Examples
    --------
    * Free fall

    Consider the dimensions mass ``M``, length ``L`` and time ``T``.
    Next, assume that ``z`` is height, ``m`` is mass, ``v`` is velocity,
    ``g`` is gravitational acceleration, ``t`` is time, ``z0`` is the
    initial height and ``v0`` is the initial velocity. In addition, take
    the set of scaling parameters formed by ``g``, ``z0`` and ``v0``.
    Finally, the nondimensional models ``ndmodels`` for the height ``z``
    are built and displayed as:

    >>> from nodimo import Variable, NonDimensionalModels
    >>> z = Variable('z', L=1, dependent=True)
    >>> m = Variable('m', M=1)
    >>> v = Variable('v', L=1, T=-1)
    >>> g = Variable('g', L=1, T=-2, scaling=True)
    >>> t = Variable('t', T=1)
    >>> z0 = Variable('z_0', L=1, scaling=True)
    >>> v0 = Variable('v_0', L=1, T=-1, scaling=True)
    >>> ndmodels = NonDimensionalModels(z, m, v, g, t, z0, v0)
    >>> ndmodels.show()
    """

    def __init__(self,
                 *variables: BasicVariable,
                 display_messages: bool = True):

        super().__init__(*variables, display_messages=display_messages)
        self._validate_scaling_variables()
        
        self.scaling_groups: list[list[BasicVariable]]
        self.nondimensional_functions: list[VariableRelation]

        self.scaling_groups = self._build_scaling_groups()
        self.nondimensional_functions = self._build_nondimensional_functions()

    def _validate_scaling_variables(self) -> None:
        """Validates the starting set of scaling variables.

        This method validates the starting set of scaling variables. If
        no variable is defined as scaling, all independent dimensional
        variables are considered scaling.

        Raises
        ------
        ValueError
            If the number of scaling variables is lower than necessary.
        """

        # If no scaling variables are defined, all independent
        # dimensional variables are considered scaling.
        if len(self.scaling_variables) == 0:
            print("No scaling variables defined")
            print("Building all possible models")

            self.scaling_variables = [var
                                      for var in self.dimensional_variables
                                      if not var.is_dependent]

        if len(self.scaling_variables) < self.dimensional_matrix.rank:
            raise ValueError(f"The model must have at least "
                             f"{self.dimensional_matrix.rank} "
                             f"scaling variables.")

    def _build_scaling_groups(self) -> list[list[BasicVariable]]:
        """Builds scaling groups from the initial scaling variables.

        Returns
        -------
        scaling_groups : list[list[Variable]]
            List containing sets of validated scaling groups.
        """

        scaling_groups = []

        # All possible scaling groups.
        all_scaling_groups = [
            list(group)
            for group in combinations(self.scaling_variables,
                                      self.dimensional_matrix.rank)
        ]

        # Find groups that form an independent set.
        for scaling_group in all_scaling_groups:
            A = _build_dimensional_matrix(scaling_group, self.dimensions)

            if A.rank() == self.dimensional_matrix.rank:
                scaling_groups.append(scaling_group)

        return scaling_groups

    def _build_nondimensional_functions(self) -> list[VariableRelation]:
        """Builds one nondimensional function for each scaling group.

        Returns
        -------
        nondimensional_functions : list[ModelFunction]
            List with one nondimensional function for each scaling
            group.
        """

        nondimensional_functions = []

        model = NonDimensionalModel(*self.variables,
                                    build_now=False,
                                    display_messages=False)
        
        # It's not necessary to validate the scaling groups.
        model._check_scaling_variables = False

        for scaling_group in self.scaling_groups:
            # Update scaling and nonscaling variables in model.
            nonscaling_variables = []

            for var in self.dimensional_variables:
                if var not in scaling_group:
                    nonscaling_variables.append(var)

            model.scaling_variables = scaling_group
            model.nonscaling_variables = nonscaling_variables

            # Reorder dimensional variables.
            model.dimensional_variables = nonscaling_variables + scaling_group

            # Rebuild and store.
            model.build_nondimensional_model()

            nondimensional_functions.append(model.nondimensional_function)

        return nondimensional_functions

    def show_nondimensional_models(self) -> None:
        """Displays scaling groups and nondimensional functions."""

        for i, function in enumerate(self.nondimensional_functions):

            if _is_running_on_jupyter:
                scaling_group_latex = R',\ '.join([sp.latex(var) for var in
                                                   self.scaling_groups[i]])
                
                scaling_group = Math(R'\text{Scaling group }'
                                     + str(i + 1)
                                     + R'\text{:}\ '
                                     + scaling_group_latex)
            else:
                scaling_group_str = sp.pretty(self.scaling_groups[i])[1:-1]
                
                scaling_group = f"Scaling group {i + 1}: " + scaling_group_str

            _show_object(scaling_group, use_custom_css=False)
            function.show()
            _print_horizontal_line()

    # Alias for the method show_nondimensional_model.
    show = show_nondimensional_models  # FIXME: show method must be overwritten here

    def _sympystr(self, printer) -> str:
        """String representation according to Sympy."""

        return "Use the 'show' method to display the models"

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        return R"\text{Use the \textit{show} method to display the models}"


# Alias for the class NonDimensionalModels.
NonDimModels = NonDimensionalModels
