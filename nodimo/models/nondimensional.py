"""This module contains the classes to create nondimensional models.

Classes
-------
NonDimensionalModel = NonDimModel
    Creates a nondimensional model from a given set of variables.
NonDimensionalModels = NonDimModels
    Creates nondimensional models from a given set of variables.
"""

import sympy as sp
from sympy import Matrix
from itertools import combinations

from nodimo.variables.variable import Variable
from nodimo.variables.group import VariableGroup
from nodimo._internal import (_is_running_on_jupyter,
                              _show_object,
                              _print_horizontal_line,
                              _build_dimensional_matrix)

from .function import ModelFunction
from .dimensional import DimensionalModel


class NonDimensionalModel(DimensionalModel):
    """Creates a nondimensional model from a given set of variables.

    This class extends the dimensional model by introducing
    nondimensional groups and the nondimensional function, which
    describes the relationship between the groups and represents the
    model.

    Attributes
    ----------
    nondimensional_groups: list[VariableGroup]
        List of nondimensional groups.
    nondimensional_function: ModelFunction
        Function that represents the nondimensional model.

    Methods
    -------
    validate_scaling_variables()
        Validates the set of scaling variables.
    build_nondimensional_model() = build()
        Builds the main characteristics of the nondimensional model.
    build_exponents_matrix()
        Builds the matrix of exponents for the nondimensional groups.
    build_nondimensional_groups()
        Builds nondimensional groups.
    show_nondimensional_function() = show()
        Displays the nondimensional function.

    Alias
    -----
    NonDimModel

    Examples
    -------
    Period of a simple pendulum:
    First, consider the dimensions mass (M), length (L) and time (T).
    Second, assume that P is period, m is mass and, g is gravitational
    acceleration, D is the pendulum's length and t0 is the initial
    angle.Third, take g and D as scaling parameters. The nondimensional
    model (ndmodel) for the period is built and displayed as:
    >>> from nodimo import Variable, NonDimensionalModel
    >>> P = Variable('P', T=1, dependent=True)
    >>> m = Variable('m', M=1)
    >>> g = Variable('g', L=1, T=-2, scaling=True)
    >>> D = Variable('D', L=1, scaling=True)
    >>> t0 = Variable('theta_0')
    >>> ndmodel = NonDimensionalModel(P, m, g, D, t0)
    >>> ndmodel.show()
    """

    def __init__(self,
                 *variables: Variable,
                 build_now: bool = True,
                 display_messages: bool = True):
        """
        Parameters
        ----------
        *variables: Variable
            Variables that constitute the model.
        build_now: bool, optional (default=True)
            If True, the variables are validated and the model is built.
        display_messages: bool, optional (default=True)
            If True, extra variables and dimensions are displayed.
        """

        super().__init__(*variables, display_messages=display_messages)

        # This attribute is used by the class NonDimensionalModels to
        # avoid the validation of the scaling variables.
        self._check_scaling_variables: bool = True

        self.nondimensional_groups: list[VariableGroup]
        self.nondimensional_function: ModelFunction

        if build_now:
            self.validate_scaling_variables()
            self.build_nondimensional_model()

    def validate_scaling_variables(self) -> None:
        """Validates the set of scaling variables.

        Raises
        ------
        ValueError
            If the number of scaling variables is lower than necessary.
        ValueError
            If the scaling variables do not form an independent set.
        """

        if len(self.scaling_variables) != self.dimensional_matrix.rank_:
            raise ValueError(f"The model must have "
                             f"{self.dimensional_matrix.rank_} "
                             f"scaling variables.")

        A = _build_dimensional_matrix(self.scaling_variables, self.dimensions)

        if A.rank() != self.dimensional_matrix.rank_:
            raise ValueError(
                "Scaling variables do not form an independent set")

    def build_nondimensional_model(self) -> None:
        """Builds the main properties of the nondimensional model."""

        if self._check_scaling_variables:
            self.validate_scaling_variables()

        self.nondimensional_groups = self.build_nondimensional_groups()

        self.nondimensional_function = ModelFunction(
            *self.nondimensional_variables,
            *self.nondimensional_groups,
            name='Pi'
        )

    # Alias for build_nondimensional_model.
    build = build_nondimensional_model

    def build_exponents_matrix(self) -> Matrix:
        """Builds the matrix of exponents for the nondimensional groups.

        Returns
        -------
        exponents_matrix: Matrix
            Matrix containing the exponents, where each row is the
            corresponding dimensional variable, and every column
            represents a group.
        
        References
        ----------
        [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
            (Butterworth-Heinemann, 2007), p. 133.
        """

        number_of_dimensions = len(self.dimensions)
        number_of_variables = len(self.dimensional_variables)

        A = _build_dimensional_matrix(self.scaling_variables,
                                      self.dimensions)
        B = _build_dimensional_matrix(self.nonscaling_variables,
                                      self.dimensions)

        # In case the dimensional matrix has linear dependent rows.
        if number_of_dimensions > self.dimensional_matrix.rank_:
            dimensional_matrix = B.row_join(A)
            _, independent_rows = dimensional_matrix.T.rref()
            A, B = A[independent_rows, :], B[independent_rows, :]

        # Components to build the matrix of exponents.
        E11 = sp.eye(number_of_variables - self.dimensional_matrix.rank_)
        E12 = sp.zeros(number_of_variables - self.dimensional_matrix.rank_,
                       self.dimensional_matrix.rank_)
        E21 = -A**-1 * B
        E22 = A**-1

        E = sp.Matrix([[E11, E12],
                       [E21, E22]])

        Z1 = sp.eye(number_of_variables - self.dimensional_matrix.rank_)
        Z2 = sp.zeros(self.dimensional_matrix.rank_,
                      number_of_variables - self.dimensional_matrix.rank_)

        Z = sp.Matrix([[Z1],
                       [Z2]])

        exponents_matrix = E * Z

        return exponents_matrix

    def build_nondimensional_groups(self) -> list[VariableGroup]:
        """Builds nondimensional groups.

        Returns
        -------
        nondimensional_groups: list[VariableGroup]
            List containing the nondimensional groups.
        """

        exponents_matrix = self.build_exponents_matrix()

        nondimensional_groups = []

        for j in range(len(self.nonscaling_variables)):

            nondimensional_groups.append(
                VariableGroup(self.dimensional_variables,
                              exponents_matrix.col(j).T,
                              check_inputs=False,
                              check_dimensions=False)
            )

        return nondimensional_groups

    def show_nondimensional_function(self) -> None:
        """Displays the nondimensional function."""

        self.nondimensional_function.show()

    # Alias for the method show_nondimensional_model.
    show = show_nondimensional_function


# Alias for the class NonDimensinalModel.
NonDimModel = NonDimensionalModel


class NonDimensionalModels(DimensionalModel):
    """Creates nondimensional models from a given set of variables.

    This class also extends the dimensional model, but its purpose is to
    gather multiple nondimensional functions built from distinct groups
    of scaling variables. It can be understood as a collection of
    nondimensional models.

    Attributes
    ----------
    scaling_groups: list[list[Variable]]
        List containing sets of validated scaling groups.
    nondimensional_functions: list[ModelFunction]
        List with one nondimensional function for each scaling group.

    Methods
    -------
    validate_scaling_variables()
        Validates the starting set of scaling variables.
    build_scaling_groups()
        Builds scaling groups from the initial scaling variables.
    build_nondimensional_functions()
        Builds one nondimensional function for each scaling group.
    show_nondimensional_functions() = show()
        Displays scaling groups and respective nondimensional functions.

    Alias
    -----
    NonDimModels

    Examples
    -------
    Free fall motion:
    First, consider the dimensions mass (M), length (L) and time (T).
    Second, assume that z is height, m is mass, v is velocity, g is
    gravitational acceleration, t is time, z0 is the initial height and
    v0 is the initial velocity. Third, take the initial set of scaling
    parameters formed by g, z0 and v0. Finally, the nondimensional
    models (ndmodels) for the height z are built and displayed as:
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

    def __init__(self, *variables: Variable, display_messages: bool = True):
        """
        Parameters
        ----------
        *variables: Variable
            Variables that constitute the model.
        display_messages: bool, optional (default=True)
            If True, extra variables and dimensions are displayed.
        """

        super().__init__(*variables, display_messages=display_messages)

        self.validate_scaling_variables()
        self.scaling_groups: list[list[Variable]] = self.build_scaling_groups()
        self.nondimensional_functions: list[ModelFunction] = (
            self.build_nondimensional_functions()
        )

    def validate_scaling_variables(self) -> None:
        """Validates the starting set of scaling variables.

        This method validates the starting set of scaling variables. If
        no variable is defined as scaling, all independent dimensional
        variables are considered scaling.

        Raises
        ------
        ValueError
            If the model does not have the minimum number of scaling
            variables.
        """

        # If no scaling variables are defined, all independent
        # dimensional variables are considered scaling.
        if len(self.scaling_variables) == 0:
            print("No scaling variables defined")
            print("Building all possible models")

            self.scaling_variables = [var
                                      for var in self.dimensional_variables
                                      if not var.is_dependent]

        if len(self.scaling_variables) < self.dimensional_matrix.rank_:
            raise ValueError(f"The model must have at least "
                             f"{self.dimensional_matrix.rank_} "
                             f"scaling variables.")

    def build_scaling_groups(self) -> list[list[Variable]]:
        """Builds scaling groups from the initial scaling variables.

        Returns
        -------
        scaling_groups: list[list[Variable]]
            List containing sets of validated scaling groups.
        """

        scaling_groups = []

        # All possible scaling groups.
        all_scaling_groups = [
            list(group)
            for group in combinations(self.scaling_variables,
                                      self.dimensional_matrix.rank_)
        ]

        # Find groups that form an independent set.
        for scaling_group in all_scaling_groups:
            A = _build_dimensional_matrix(scaling_group, self.dimensions)

            if A.rank() == self.dimensional_matrix.rank_:
                scaling_groups.append(scaling_group)

        return scaling_groups

    def build_nondimensional_functions(self) -> list[ModelFunction]:
        """Builds one nondimensional function for each scaling group.

        Returns
        -------
        nondimensional_functions: list[ModelFunction]
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

    def show_nondimensional_functions(self) -> None:
        """Displays scaling groups and nondimensional functions."""

        for i, function in enumerate(self.nondimensional_functions):

            if _is_running_on_jupyter:
                scaling_group_latex = R',\ '.join([sp.latex(var) for var in
                                                   self.scaling_groups[i]])
                
                scaling_group = (R'\text{Scaling group }'
                                 + str(i + 1)
                                 + R'\text{:}\ '
                                 + scaling_group_latex)
            else:
                scaling_group_str = sp.pretty(self.scaling_groups[i])[1:-1]
                
                scaling_group = f"Scaling group {i + 1}: " + scaling_group_str

            _show_object(scaling_group)
            function.show()
            _print_horizontal_line()

    # Alias for the method show_nondimensional_model.
    show = show_nondimensional_functions


# Alias for the class NonDimensionalModels.
NonDimModels = NonDimensionalModels
