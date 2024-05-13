"""
===========================
Basic (:mod:`nodimo.basic`)
===========================

This module contains base classes for Nodimo.

Classes
-------
BasicGroup
    Base class for classes created with variables.
"""

from sympy import sstr, srepr, pretty, S, Rational, Matrix, ImmutableDenseMatrix, zeros, eye
from sympy.core._print_helpers import Printable
from sympy.printing.pretty.stringpict import prettyForm
from typing import Union, Optional

from nodimo.variable import Variable, OneVar
from nodimo._internal import _show_object, _show_warning, UnrelatedVariableWarning


DimensionType = Union[tuple[str], dict[str, Rational]]


class Collection:  # TODO: I couldn't make it inherit from tuple like I wanted. But sympy has a Tuple class that might work well.
    """Collection of variables.

    This class contains common attributes and methods that are used by
    classes created with a collection of variables.

    Parameters
    ----------
    *variables : Variable
        Variables that constitute the collection.

    Attributes
    ----------
    variables : tuple[Variable]
        Tuple with the variables that constitute the collection.
    dimensions : tuple[str] or dict[str, Rational]
        Tuple with the dimensions' names.
    """

    def __init__(self, *variables: Variable):

        self._variables: tuple[Variable] = variables
        self._dimensions: DimensionType

        # Attributes to be used in child classes.
        self._base_variables: tuple[Variable]
        
        self._scaling_variables: tuple[Variable]
        self._nonscaling_variables: tuple[Variable]
        
        self._dependent_variables: tuple[Variable]
        self._independent_variables: tuple[Variable]
        
        self._has_one: bool
        self._has_product: bool
        self._is_independent: bool

        self._raw_matrix: list[list[Rational]]
        self._matrix: ImmutableDenseMatrix
        self._rank: int
        self._independent_rows: tuple[int]
        self._submatrices: dict[Variable, ImmutableDenseMatrix]
        
        self._set_collection_properties()

    @property
    def variables(self) -> tuple[Variable]:
        return self._variables

    @property
    def dimensions(self) -> DimensionType:
        return self._dimensions

    def _set_collection_properties(self):
        """Sets the collection properties."""

        self._set_dimensions()

    def _set_dimensions(self):
        """Sets the dimensions' names."""

        dimensions = []

        for var in self._variables:
            for dim in var.dimensions.keys():
                if dim not in dimensions:
                    dimensions.append(dim)

        self._dimensions = tuple(dimensions)

    @classmethod
    def _clear_ones(self, *variables: Variable) -> tuple[Variable]:
        """Removes instances of OneVar."""

        new_variables = []
        for var in variables:
            if not isinstance(var, OneVar):
                new_variables.append(var)

        return tuple(new_variables)

    def _disassemble_variables(self):
        """Disassembles variables created from multiple base variables.
        
        Disassembling is an important step in simplifying expressions.
        """

        self._has_one = False
        self._has_product = False
        disassembled_variables = []
        for var in self._variables:
            if var._is_product:
                disassembled_variables.extend(var._variables)
                self._has_product = True
            elif var._is_one:
                self._has_one = True
            else:
                disassembled_variables.append(var)

        self._disassembled_variables = tuple(disassembled_variables)

    def _set_base_variables(self):
        """Determines the base variables."""

        if not hasattr(self, '_disassembled_variables'):
            self._disassemble_variables()

        base_variables = []
        for var in self._disassembled_variables:
            if var._is_power:
                base_var = var._variable
            else:
                base_var = var
            
            if base_var not in base_variables:
                base_variables.append(base_var)

        self._base_variables = tuple(base_variables)
        self._is_independent = len(self._base_variables) == len(self._disassembled_variables)  # TODO: Should i include the Ones?

    def _set_scaling_variables(self):
        """Separates scaling and nonscaling variables."""

        scaling_variables = []
        nonscaling_variables = []
        for var in self._variables:
            if var.is_scaling:
                scaling_variables.append(var)
            else:
                nonscaling_variables.append(var)

        self._scaling_variables = tuple(scaling_variables)
        self._nonscaling_variables = tuple(nonscaling_variables)

    def _set_dependent_variables(self):
        """Separates dependent and independent variables."""

        dependent_variables = []
        independent_variables = []
        for var in self.variables:
            if var.is_dependent:
                dependent_variables.append(var)
            else:
                independent_variables.append(var)

        self._dependent_variables = tuple(dependent_variables)
        self._independent_variables = tuple(independent_variables)

    def _build_matrix(self):
        """Builds a dimensional matrix from the variables."""
    
        raw_matrix = []
    
        for dim in self._dimensions:
            dim_exponents = []
            for var in self._variables:
                if dim in var.dimensions.keys():
                    dim_exponents.append(var.dimensions[dim])
                else:
                    dim_exponents.append(S.Zero)
            raw_matrix.append(dim_exponents)

        self._raw_matrix = raw_matrix
        self._matrix = ImmutableDenseMatrix(raw_matrix)

    def _set_matrix_rank(self):
        
        if not hasattr(self, '_matrix'):
            self._build_matrix()
        
        self._rank = self._matrix.rank()

    def _set_matrix_independent_rows(self):

        if not hasattr(self, '_rank'):
            self._set_matrix_rank()

        if len(self._dimensions) > self._rank:
            _, independent_rows = self._matrix.T.rref()
        else:
            independent_rows = tuple(range(len(self._dimensions)))
        
        self._independent_rows = independent_rows

    def _build_submatrices(self):
        """Builds one column matrix for each variable."""

        if not hasattr(self, '_matrix'):
            self._build_matrix()

        submatrices = []
        for i, var in enumerate(self._variables):
            submatrices.append((var, self._matrix.col(i)))

        self._submatrices = dict(submatrices)

    def _get_submatrix(self, *variables) -> ImmutableDenseMatrix:
        """Combines the variables submatrices into one submatrix.

        Parameters
        ----------
        *variables : BasicVariable
            Variables used to build the submatrix.

        Returns
        -------
        submatrix : ImmutableDenseMatrix
            The submatrix built from the given variables.

        Raises
        ValueError
            If the given variables are not all part of the dimensional matrix.
        """

        if not set(variables).issubset(set(self._variables)):
            raise ValueError(f"'{variables}' is not a subset of '{self._variables}'")
        elif not hasattr(self, '_submatrices'):
            self._build_submatrices()

        submatrices = [self._submatrices[var] for var in variables]
        submatrix = ImmutableDenseMatrix.hstack(*submatrices)

        return submatrix

    def _key(self) -> tuple:

        return (frozenset(self._variables),)

    def __hash__(self) -> int:

        return hash(self._key())

    def __eq__(self, other) -> bool:

        if self is other:
            return True
        elif isinstance(other, type(self)):
            return self._key() == other._key()
        return False
    
    def __contains__(self, item) -> bool:

        return self._variables.__contains__(item)

    def __len__(self) -> int:

        return self._variables.__len__()

    def __iter__(self):

        return self._variables.__iter__()

    def __next__(self):

        return self.__iter__().__next__() 

    def __str__(self) -> str:

        class_name = type(self).__name__
        variables_str = ', '.join(sstr(var) for var in self._variables)

        return f'{class_name}({variables_str})'

    def __repr__(self) -> str:

        class_name = type(self).__name__
        variables_repr = ', '.join(srepr(var) for var in self._variables)

        return f'{class_name}({variables_repr})'


class Group(Collection):
    """Group of variables.

    Equivalent to a Collection without duplicate variables.
    """

    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._set_group_properties()

    def _set_group_properties(self):
        """Sets the group properties."""

        self._remove_duplicate_variables()

    def _remove_duplicate_variables(self):
        """Removes duplicate variables, keeping the order."""

        new_variables = []
        
        for var in self._variables:
            if var not in new_variables:
                new_variables.append(var)

        self._variables = tuple(new_variables)


class PrintableGroup(Printable, Group):
    """Printable group of variables.

    Equivalent to Group, but it inherits from the Sympy Printable class
    the ability to be displayed in a pretty format.

    Methods
    -------
    show()
        Displays the group in a pretty format.
    """

    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._set_printgroup_properties()

    @property
    def symbolic(self):
        return self._symbolic

    def show(self, use_custom_css: bool = True):
        """Displays the group in a pretty format."""

        _show_object(self, use_custom_css=use_custom_css)  # TODO: Include use_custom_css in the future global settings.

    def _set_printgroup_properties(self):
        """Sets the printable group properties."""

        self._build_symbolic()

    def _build_symbolic(self):
        """Builds symbolic representation in Sympy."""

        self._symbolic = self._variables

    def _sympy_(self):
        """Sympified group."""

        return self._symbolic

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        return super().__repr__()
    
    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy."""

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.

        return printer._print(self._symbolic)

    _latex = _pretty = _sympystr


class HomogeneousGroup(Group):
    """Dimensionally homogeneous group of variables.

    Equivalent to Group, but it is dimmensionally homogenous.

    Parameters
    ----------
    *variables : BasicVariable
        Variables that constitute the group.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        Tuple with the variables.
    dimensions : tuple[str]
        Tuple with the dimensions' names.

    Warns
    -----
    UnrelatedVariableWarning
        Discarded variables.
    """

    def __init__(self, *variables: Variable):
        
        super().__init__(*variables)
        self._set_homogroup_properties()

    def _set_homogroup_properties(self):
        """Sets the group properties."""

        self._clear_unrelated_variables()

    def _clear_unrelated_variables(self):
        """Removes unrelated variables.

        Unrelated variables are the only ones in the set of variables to have
        a particular dimension.
        """

        clear_variables = list(self._variables)
        unrelated_variables = []
        for _ in self._variables:
            self._build_matrix()
            unr_var = None
            for row in self._raw_matrix:
                row_bool = [bool(exp) for exp in row]
                if sum(row_bool) == 1:
                    unr_var = clear_variables[row_bool.index(True)]
                    if unr_var not in unrelated_variables:
                        unrelated_variables.append(unr_var)
                        clear_variables.remove(unr_var)
                        self._variables = tuple(clear_variables)
                        self._set_dimensions()
                        break
            if unr_var is None:
                break

        if len(unrelated_variables) > 0:
            _show_warning(f"Discarded variables → "
                          f"{pretty(set(unrelated_variables))[1:-1]}",
                          UnrelatedVariableWarning)


class ScalingGroup(PrintableGroup):
    
    def __init__(self, *variables: Variable, id_number: Optional[int] = None):

        super().__init__(*variables)
        self._set_scgroup_variables()
        self._set_matrix_rank()
        self._validate_scaling_group()
        self._id_number: int = id_number

    def _set_scgroup_variables(self):
        """Sets all variables in the group as scaling."""

        new_variables = []
        for var in self._variables:
            if var.is_scaling:
                new_var = var
            else:
                new_var = var._copy()
                new_var.is_scaling = True
            new_variables.append(new_var)
        
        self._variables = tuple(new_variables)

    def _validate_scaling_group(self):
        if len(self._variables) != self._rank:
            raise ValueError("Scaling variables are not dimensionally independent")

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variables_repr = ', '.join(srepr(var) for var in self._variables)
        id_number_repr = f', id_number={self._id_number}' if self._id_number else ''

        return f'{class_name}({variables_repr}{id_number_repr})'

    def _printmethod(self, printer):
        """String representation according to Sympy."""

        id_number = f' {self._id_number}' if self._id_number else ''
        scgroup = printer._print(f"Scaling group{id_number} ")
        variables = printer._print(self._variables)

        if printer.printmethod == '_pretty':
            return prettyForm(*scgroup.right(variables))
        else:
            return scgroup + variables

    _latex = _pretty = _sympystr = _printmethod


class TransformationGroup(HomogeneousGroup):
    """Blueprint for the transformation of a homogeneous group.

    A TransformationGroup sets the layout fot the transformation of a
    group of variables into another group by using scaling variables as
    transformation parameters. Every variable of the new group is a
    product between one nonscaling variable and the set of scaling
    variables.

    Parameters
    ----------
    *variables : BasicVariable
        Variables to be transformed.

    Attributes
    ----------
    variables : empty tuple
        Tuple to be populated with the transformation result.
    dimensions : empty dictionary
        Dictionary to be populated with the transformation result.
    xvariables : tuple[BasicVariable]
        Tuple with the variables to be transformed.
    scaling_variables : tuple[BasicVariable]
        Tuple with scaling variables.
    nonscaling_variables : tuple[BasicVariable]
        Tuple with nonscaling variables.

    Raises
    ------
    ValueError
        If the number of scaling variables is not adequate.
    ValueError
        If the scaling variables do not form an independent set.
    """
    
    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._xvariables: tuple[Variable]
        self._set_transfgroup_properties()

    def _set_transfgroup_properties(self):

        self._set_scaling_variables()
        self._set_matrix_independent_rows()
        self._set_scaling_matrix()
        self._validate_transfgroup_variables()
        self._xvariables = tuple(list(self._variables))
        self._variables = ()
        self._dimensions = {}

    def _set_scaling_matrix(self):
        """Builds scaling and nonscaling matrices."""

        scaling_matrix = self._get_submatrix(*self._scaling_variables)
        nonscaling_matrix = self._get_submatrix(*self._nonscaling_variables)

        self._scaling_matrix = scaling_matrix[self._independent_rows, :]
        self._nonscaling_matrix = nonscaling_matrix[self._independent_rows, :]

    def _validate_transfgroup_variables(self):
        """Validates the scaling variables."""
        
        if self._scaling_matrix.rank() != self._rank:
            raise ValueError(
                f"The group must have {self._rank} "
                f"dimensionally independent scaling variables"
            )

    def _key(self) -> tuple:

        return (frozenset(self._xvariables),)

    def __str__(self) -> str:

        class_name = type(self).__name__
        variables_str = ', '.join(sstr(var) for var in self._xvariables)

        return f'{class_name}({variables_str})'
    
    def __repr__(self) -> str:

        class_name = type(self).__name__
        variables_repr = ', '.join(srepr(var) for var in self._xvariables)

        return f'{class_name}({variables_repr})'


# An generalization to be implemented later.
# class DimensionalGroup(Group):
# 
#     def __init__(self, scaling_group: ScalingGroup, dimensions: Optional[dict[str, int]] = {}):  # dimensions == {} must be equivalent to NonDimensionalGroup implementation
# 
#         pass


class NonDimensionalGroup(TransformationGroup):  # When DimensionalGroup is implemented, this should inherit from it.
    """Nondimensional group created from a homogeneous group.

    This class creates a group of nondimensinal variables from a
    homogeneous given group of variables. It does that using the
    TransformationGroup layout.

    Parameters
    ----------
    *variables : BasicVariable
        Variables to be transformed.

    Attributes
    ----------
    variables : tuple[BasicVariable]
        Tuple with nondimensional variables.
    dimensions : dict[str, int]
        Empty dictionary that represents the nondimensional group.
    xvariables : tuple[BasicVariable]
        Tuple with the variables to be transformed.
    scaling_variables : tuple[BasicVariable]
        Tuple with scaling variables.
    nonscaling_variables : tuple[BasicVariable]
        Tuple with nonscaling variables.

    Raises
    ------
    ValueError
        If the number of scaling variables is not adequate.
    ValueError
        If the scaling variables do not form an independent set.
    """
    
    def __init__(self, *variables: Variable):

        super().__init__(*variables)
        self._nondim_products: tuple[Variable]
        self._set_nondimgroup_properties()
    
    def _set_nondimgroup_properties(self):
        """Sets the group properties."""
        
        self._separate_dimensional_variables()
        self._calculate_exponents()
        self._build_nondimensional_products()
    
    def _separate_dimensional_variables(self):  # TODO: Transfer this method to Collection
        """Retains already nondimensional variables."""
        
        dimensional_variables = []
        nondimensional_variables = []
        for var in self._xvariables:
            if var.is_nondimensional:
                nondimensional_variables.append(var)
            else:
                dimensional_variables.append(var)

        if len(nondimensional_variables) > 0:
            self._variables = tuple(dimensional_variables)
            self._set_dimensions()
            self._set_scaling_variables()
            self._set_scaling_matrix()
            self._xvariables = tuple(list(self._variables))
            self._variables = tuple(nondimensional_variables)
            self._dimensions = {}

    def _calculate_exponents(self):
        """Determines the exponents for the scaling variables.

        References
        ----------
        .. [1] Thomas Szirtes, Applied Dimensional Analysis and Modeling
               (Butterworth-Heinemann, 2007), p. 133.
        """

        nvars = len(self._xvariables)
        rank = self._rank

        A = self._scaling_matrix
        B = self._nonscaling_matrix

        E11 = eye(nvars - rank)
        E12 = zeros(nvars - rank, rank)
        E21 = -A**-1 * B
        E22 = A**-1
        E = Matrix([[E11, E12],
                    [E21, E22]])

        Z1 = eye(nvars - rank)
        Z2 = zeros(rank, nvars - rank)
        Z = Matrix([[Z1],
                    [Z2]])

        exponents = E * Z

        self._exponents = exponents.as_immutable()

    def _build_nondimensional_products(self):
        """Builds the nondimensional variables."""

        from .product import Product
        from .power import Power

        variables = self._nonscaling_variables + self._scaling_variables
        self._calculate_exponents()
        nondim_products = []

        for j in range(len(self._nonscaling_variables)):
            factors = []
            for var, exp in zip(variables, self._exponents.col(j)):
                factors.append(Power(var, exp))
            nondim_products.append(Product(*factors))

        self._nondim_products = tuple(nondim_products)
        self._variables += self._nondim_products

    def _set_asdependent_from_arguments(self):
        """Sets nondimensional products as dependent from arguments.

        Nondimensional product is set as dependent if it contains at
        least one dependent variable in its expression.
        """

        for prod in self._nondim_products:
            prod.is_dependent = any(var.is_dependent for var in prod._variables)
