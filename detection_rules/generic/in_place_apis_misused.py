import ast
from detection_rules.smell import Smell


class InPlaceAPIsMisusedSmell(Smell):
    """
    Detects cases where Pandas in-place APIs are used incorrectly,
    potentially causing confusion about memory usage.

    Example of code smell:
        df.drop(columns=["column_name"], inplace=False)  # Potential misuse

    Preferred alternative:
        Use either:
        - df = df.drop(columns=["column_name"])  # Assign result to a variable
        - df.drop(columns=["column_name"], inplace=True)
          # Explicitly use in-place operation
    """

    def __init__(self):
        super().__init__(
            name="in_place_apis_misused",
            description=(
                "Check whether the result of the operation is assigned to "
                "a variable or the in-place parameter is set. "
                "Some developers mistakenly assume in-place "
                "operations always save memory."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Check for Pandas library
        pandas_alias = extracted_data["libraries"].get("pandas")
        if not pandas_alias:
            return smells

        dataframe_variables = extracted_data.get("dataframe_variables", [])
        dataframe_methods = extracted_data.get("dataframe_methods", [])

        # Traverse AST nodes
        for node in ast.walk(ast_node):
            # Identify calls like `df.method(...)`
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and hasattr(node.func.value, "id")
                and node.func.value.id in dataframe_variables
                and node.func.attr in dataframe_methods
            ):
                # Check if the call uses the "inplace" parameter
                inplace_flag = None
                for keyword in getattr(node, "keywords", []):
                    if keyword.arg == "inplace":
                        inplace_flag = getattr(keyword.value, "value", None)

                # Flag cases where "inplace" is explicitly set to False
                if inplace_flag is False:
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                f"Explicitly setting `inplace=False`"
                                f"for `{node.func.attr}`"
                                "may cause confusion. Consider assigning the "
                                "result to a variable or explicitly using "
                                "`inplace=True`."
                            ),
                        )
                    )

                # Flag cases where "inplace" is
                # not set and the result is not assigned
                if inplace_flag is None and not self._is_assignment(
                    node, ast_node
                ):
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                f"The result of the `{node.func.attr}` method "
                                "is not assigned to a variable, "
                                "and the `inplace` parameter is not "
                                "explicitly set. Consider assigning "
                                "the result or setting `inplace=True`."
                            ),
                        )
                    )

        return smells

    def _is_assignment(self, node: ast.Call, root_node: ast.AST) -> bool:
        """
        Determines if the result of a method call is assigned to a variable.

        Parameters:
        - node: The method call node to check.
        - root_node: The root AST node of the function or file.

        Returns:
        - bool: True if the method call result is assigned, False otherwise.
        """
        for parent in ast.walk(root_node):
            if isinstance(parent, ast.Assign):
                # Check if the current node is assigned to a variable
                if parent.value is node:  # Direct assignment check
                    return True
        return False
