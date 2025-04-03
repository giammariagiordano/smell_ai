import ast
from detection_rules.smell import Smell


class MatrixMultiplicationAPIMisused(Smell):
    """
    Detects misuse of the `dot()` function for matrix multiplication in NumPy.

    Example of code smell:
        np.dot([[1, 2], [3, 4]], [[5, 6], [7, 8]])  # Deprecated usage

    Preferred alternative:
        # Explicit and recommended
        np.matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]])
    """

    def __init__(self):
        super().__init__(
            name="matrix_multiplication_api_misused",
            description="Using `dot()` for matrix multiplication"
            " is discouraged. Use `np.matmul` instead.",
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Ensure NumPy library is used
        numpy_alias = extracted_data["libraries"].get("numpy")
        if not numpy_alias:
            return smells

        lines = extracted_data.get("lines", {})

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call) and isinstance(
                node.func, ast.Attribute
            ):
                # Check if `dot` is called using the NumPy alias
                if (
                    node.func.attr == "dot"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == numpy_alias
                ):
                    # Check if the `dot()` call arguments involve matrices
                    if self._is_matrix_multiplication(node):
                        code_snippet = lines.get(
                            node.lineno, "<Code not available>"
                        )
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info=(
                                    f"Detected misuse of `dot()`"
                                    " for matrix multiplication. "
                                    f"Consider using `np.matmul` instead. "
                                    f"Code: {code_snippet}"
                                ),
                            )
                        )
        return smells

    def _is_matrix_multiplication(self, node: ast.Call) -> bool:
        """
        Checks if the arguments of a `dot()` function call represent matrices.

        Parameters:
        - node (ast.Call): The AST node of the `dot()` function call.

        Returns:
        - bool: True if matrix multiplication is detected, False otherwise.
        """
        if not hasattr(node, "args") or len(node.args) < 2:
            return False

        for arg in node.args:
            # Case 1: Check if the argument is a matrix literal (list of lists)
            if isinstance(arg, ast.List) and all(
                isinstance(el, ast.List) for el in arg.elts
            ):
                return True
            # Case 2: Check if the argument is a variable representing a matrix
            elif isinstance(arg, ast.Name):
                return True

        return False
