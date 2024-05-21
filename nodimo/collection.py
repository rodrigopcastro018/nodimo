from sympy import sstr, latex, S, Number, ImmutableDenseMatrix, sympify
from sympy.printing.pretty.stringpict import prettyForm

from nodimo.variable import Variable, OneVar
from nodimo._internal import _show_object


class Collection:
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
    dimensions : dict[str, Number]
        Dictionary with all dimensions' names as keys. If all variables
        have the same dimensions, the exponents are the dictionary's
        values. Otherwise, the dictionary's values are NaN.

    Methods
    -------
    show()
        Displays the collection in a pretty format.
    """

    def __init__(self, *variables: Variable):

        # Main attributes.
        self._variables: tuple[Variable] = variables
        self._dimensions: dict[str, Number]
        self._is_nondimensional: bool

        # Attributes to be used in child classes.
        self._disassembled_variables: tuple[Variable]
        self._base_variables: tuple[Variable]
        
        self._scaling_variables: tuple[Variable]
        self._nonscaling_variables: tuple[Variable]
        
        self._dependent_variables: tuple[Variable]
        self._independent_variables: tuple[Variable]

        self._dimensional_variables: tuple[Variable]
        self._nondimensional_variables: tuple[Variable]

        self._is_independent: bool  #TODO: Implement this in a different method

        self._raw_matrix: list[list[Number]]
        self._matrix: ImmutableDenseMatrix
        self._rank: int
        self._independent_rows: tuple[int]
        self._submatrices: dict[Variable, ImmutableDenseMatrix]

        self._set_collection()

    @property
    def variables(self) -> tuple[Variable]:
        return self._variables

    @property
    def dimensions(self) -> dict[str, Number]:
        return self._dimensions

    def show(self, use_custom_css: bool = True):
        _show_object(self, use_custom_css=use_custom_css)  # TODO: Include use_custom_css in the future global settings.
    
    def _set_collection(self):
        self._set_collection_dimensions()

    def _set_collection_dimensions(self):
        dimensions = {}
        for var in self._variables:
            for dim in var.dimensions:
                if dim not in dimensions:
                    dimensions[dim] = S.NaN

        for dim in dimensions:
            same_dim = []
            for i, var in enumerate(self._variables):
                if dim not in var.dimensions:
                    same_dim.append(False)
                    break
                if i > 0:
                    same_dim.append(var.dimensions[dim] == var_ref.dimensions[dim])
                var_ref = var
            if all(same_dim):
                dimensions[dim] = var_ref.dimensions[dim]

        self._dimensions = dimensions
        self._is_nondimensional = all(dim == 0 for dim in dimensions.values())

    def _set_dimensions(self, **dimensions: int):
        """Reserved for subclasses that need dimensions setting."""

        # Validate input dimensions in face of the collection's.
        var = Variable('', **dimensions)
        if not set(var.dimensions).issubset(set(self._dimensions)):
            invalid_dimensions = []
            for dim in var.dimensions:
                if dim not in self._dimensions:
                    invalid_dimensions.append(dim)
            raise ValueError(f"Invalid dimensions ({str(invalid_dimensions)[1:-1]})")

        group_dimensions = var.dimensions
        for dim in self._dimensions:
            if dim not in var.dimensions:
                group_dimensions[dim] = S.Zero

        self._dimensions = group_dimensions
        self._is_nondimensional = var.is_nondimensional

    def _clear_null_dimensions(self):
        """Removes dimensions with null exponents."""

        for dim, exp in self._dimensions.copy().items():
            if exp == 0:
                del self._dimensions[dim]

    def _clear_ones(self):
        """Removes instances of OneVar."""

        clear_variables = []
        for var in self._variables:
            if not isinstance(var, OneVar):
                clear_variables.append(var)

        self._variables = tuple(clear_variables)

    def _set_disassembled_variables(self):
        """Determines all instances of Variable, OneVar and Power.

        It does that by disassembling instances of Product.
        """

        disassembled_variables = []
        for var in self._variables:
            if var._is_product:
                disassembled_variables.extend(var.variables)
            else:
                disassembled_variables.append(var)

        self._disassembled_variables = tuple(disassembled_variables)

    def _set_base_variables(self):
        """Determines all instances of Variable."""
        
        if not hasattr(self, '_disassembled_variables'):
            self._set_disassembled_variables()

        base_variables = []
        for var in self._disassembled_variables:
            if var._is_power:
                base_var = var._variable
            else:
                base_var = var
            
            if base_var not in base_variables and not base_var._is_one:
                base_variables.append(base_var)

        self._base_variables = tuple(base_variables)
    
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

    def _set_dimensional_variables(self):
        """Separates dimensional and nondimensional variables."""

        dimensional_variables = []
        nondimensional_variables = []
        for var in self._variables:
            if var.is_nondimensional:
                nondimensional_variables.append(var)
            else:
                dimensional_variables.append(var)

        self._dimensional_variables = tuple(dimensional_variables)
        self._nondimensional_variables = tuple(nondimensional_variables)
    
    def _set_matrix(self):
        """Builds basic dimensional matrix."""

        raw_matrix = []
        for dim in self._dimensions:
            dim_exponents = []
            for var in self._variables:
                if dim in var.dimensions:
                    dim_exponents.append(var.dimensions[dim])
                else:
                    dim_exponents.append(S.Zero)
            raw_matrix.append(dim_exponents)

        self._raw_matrix = raw_matrix
        self._matrix = ImmutableDenseMatrix(raw_matrix)

    def _set_matrix_rank(self):
        if not hasattr(self, '_matrix'):
            self._set_matrix()
        
        self._rank = self._matrix.rank()

    def _set_matrix_independent_rows(self):
        if not hasattr(self, '_rank'):
            self._set_matrix_rank()

        if len(self._dimensions) > self._rank:
            _, independent_rows = self._matrix.T.rref()
        else:
            independent_rows = tuple(range(len(self._dimensions)))
        
        self._independent_rows = independent_rows

    def _set_submatrices(self):
        """Builds one column matrix for each variable."""

        if not hasattr(self, '_matrix'):
            self._set_matrix()

        submatrices = []
        for i, var in enumerate(self._variables):
            submatrices.append((var, self._matrix.col(i)))

        self._submatrices = dict(submatrices)

    def _get_submatrix(self, *variables) -> ImmutableDenseMatrix:
        """Combines the variables' submatrices into one submatrix.

        Parameters
        ----------
        *variables : BasicVariable
            Variables used to build the submatrix.

        Returns
        -------
        submatrix : ImmutableDenseMatrix
            The submatrix built from the given variables.

        Raises
        ------
        ValueError
            If the given variables are not all part of the collection.
        """

        if not set(variables).issubset(set(self._variables)):
            raise ValueError(f"'{variables}' is not a subset of '{self._variables}'")
        elif not hasattr(self, '_submatrices'):
            self._set_submatrices()

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
        return sstr(self)

    __repr__ = __str__

    def _repr_latex_(self):
        """Latex representation according to IPython/Jupyter."""

        return f'$\\displaystyle {latex(self)}$'
    
    def _sympy_(self):
        return sympify(self._variables)

    def _sympyrepr(self, printer) -> str:
        """Developer string representation according to Sympy."""

        class_name = type(self).__name__
        variables = ', '.join(printer._print(var) for var in self._variables)

        return f'{class_name}({variables})'

    def _sympystr(self, printer) -> str:
        """User string representation according to Sympy."""

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.
        class_name = printer._print(type(self).__name__)
        variables = ', '.join(printer._print(var) for var in self._variables)

        return f'{class_name}({variables})'

    def _latex(self, printer) -> str:
        """Latex representation according to Sympy."""

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.
        class_name = printer._print(type(self).__name__)
        variables = R',\ '.join(printer._print(var) for var in self._variables)

        return f'{class_name}\\left({variables}\\right)'

    def _pretty(self, printer) -> prettyForm:
        """Pretty representation according to Sympy."""

        printer.set_global_settings(root_notation=False)  # TODO: Include root_notation in the future global settings.
        class_name = printer._print(type(self).__name__)

        variables = prettyForm('')
        for i, var in enumerate(self._variables):
            sep = ', ' if i > 0 else ''
            variables = prettyForm(*variables.right(sep, printer._print(var)))
        variables = prettyForm(*variables.parens())

        return prettyForm(*class_name.right(variables))
