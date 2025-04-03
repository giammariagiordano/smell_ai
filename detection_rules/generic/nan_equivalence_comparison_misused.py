import ast
from detection_rules.smell import Smell


class NanEquivalenceComparisonMisusedSmell(Smell):
    """
    Detects cases where NumPy's NaN values are compared
    directly using equivalence operators,
    which is incorrect as NaN is not equivalent to itself.

    Example of code smell:
        if np.nan == value:  # Incorrect
        if value != np.nan:  # Incorrect

    Preferred alternative:
        Use NumPy functions like np.isnan() for proper NaN checks:
        if np.isnan(value):  # Correct
    """

    def __init__(self):
        super().__init__(
            name="nan_equivalence_comparison_misused",
            description=(
                "Direct equivalence comparisons with NaN should be avoided. "
                "Use functions like np.isnan() instead."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        library_name = extracted_data["libraries"].get("numpy")
        if not library_name:
            return smells

        # Traverse AST nodes
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Compare):
                # Check if NaN is misused in equivalence comparison
                if self._has_nan_comparison(node, library_name):
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                "Direct equivalence comparison with NaN "
                                "detected. Use np.isnan() instead."
                            ),
                        )
                    )

        return smells

    def _has_nan_comparison(
        self, node: ast.Compare, library_name: str
    ) -> bool:
        """
        Checks if NaN is used in equivalence or non-equivalence comparisons.

        Parameters:
        - node: An AST Compare node.
        - library_name: The alias used for NumPy (e.g., "np").

        Returns:
        - True if NaN misuse is detected, False otherwise.
        """
        # Check left-hand side of the comparison
        if self._is_nan(node.left, library_name):
            return True

        # Check comparators in the comparison (e.g., value != np.nan)
        for comparator in node.comparators:
            if self._is_nan(comparator, library_name):
                return True

        return False

    def _is_nan(self, node: ast.AST, library_name: str) -> bool:
        """
        Determines if a node represents a reference to np.nan.

        Parameters:
        - node: An AST node to check.
        - library_name: The alias used for NumPy (e.g., "np").

        Returns:
        - True if the node represents np.nan, False otherwise.
        """
        # Handle cases like np.nan
        if isinstance(node, ast.Attribute) and node.attr == "nan":
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == library_name
            ):
                return True

        # Handle direct imports like "from numpy import nan"
        if isinstance(node, ast.Name) and node.id == "nan":
            return True

        return False
