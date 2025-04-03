import ast
from typing import Optional
from detection_rules.smell import Smell


class UnnecessaryIterationSmell(Smell):
    """
    Detects unnecessary iterations or inefficient operations on Pandas objects,
    such as using `iterrows()`, `itertuples()`, `apply()`
    , or `applymap()` in loops.

    Example of code smell:
        for index, row in df.iterrows():  # Inefficient
            df["column"] = row["value"]

        while condition:
            df["b"] = df["a"].apply(lambda x: x + 1)  # Inefficient

    Preferred alternative:
        Use vectorized Pandas operations (e.g., `df["column"] = df["value"]`).
    """

    def __init__(self):
        super().__init__(
            name="unnecessary_iteration",
            description=(
                "Iterating through Pandas objects or using "
                "inefficient operations like `apply` is generally slow. "
                "Use built-in vectorized methods (e.g., join, groupby) "
                "instead of loops. "
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

        dataframe_variables = set(
            extracted_data.get("dataframe_variables", [])
        )
        inefficient_methods = {"iterrows", "itertuples", "apply", "applymap"}

        loop_nodes = [
            node
            for node in ast.walk(ast_node)
            if isinstance(node, (ast.For, ast.While))
        ]

        for loop_node in loop_nodes:
            if isinstance(loop_node, ast.For):
                # Check for inefficient iterable in `for` loops
                if self._is_inefficient_iterable(
                    loop_node, dataframe_variables, inefficient_methods
                ):
                    smells.append(
                        self.format_smell(
                            line=loop_node.lineno,
                            additional_info=(
                                "Inefficient iteration detected. "
                                "Consider using vectorized operations instead."
                            ),
                        )
                    )
                    # Skip further checks for this
                    # loop since it's already detected
                    continue

            # Check the loop body for inefficient operations
            inefficient_operation = self._has_inefficient_operations(
                loop_node, dataframe_variables, inefficient_methods
            )
            if inefficient_operation:
                smells.append(
                    self.format_smell(
                        line=inefficient_operation.lineno,
                        additional_info=(
                            "Inefficient operation detected inside the loop. "
                            "Consider using vectorized operations instead."
                        ),
                    )
                )

        return smells

    def _is_dataframe(
        self, node: ast.AST, dataframe_variables: set[str]
    ) -> bool:
        """
        Checks if the given node represents a DataFrame
        variable or a subscript (e.g., df["a"]).
        """
        if isinstance(node, ast.Name) and node.id in dataframe_variables:
            return True

        # Handle subscript (e.g., df["a"])
        if isinstance(node, ast.Subscript) and isinstance(
            node.value, ast.Name
        ):
            if node.value.id in dataframe_variables:
                return True

        return False

    def _is_inefficient_iterable(
        self,
        node: ast.For,
        dataframe_variables: set[str],
        inefficient_methods: set[str],
    ) -> bool:
        """
        Checks if a `for` loop iterates over an
        inefficient method (e.g., `iterrows`).
        """
        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Attribute)
            and node.iter.func.attr in inefficient_methods
            and self._is_dataframe(node.iter.func.value, dataframe_variables)
        ):
            return True
        return False

    def _has_inefficient_operations(
        self,
        loop_node: ast.AST,
        dataframe_variables: set[str],
        inefficient_methods: set[str],
    ) -> Optional[ast.Call]:
        """
        Checks if the loop body contains
        inefficient operations on DataFrame objects
        and returns the node of the first inefficient operation found.

        Parameters:
        - loop_node: The AST node representing the loop (For or While).
        - dataframe_variables: Set of known DataFrame variable names.
        - inefficient_methods: Set of methods considered inefficient.

        Returns:
        - ast.Call: The node of the first inefficient operation found, or None.
        """
        for body_node in ast.walk(loop_node):
            if isinstance(body_node, ast.Call):
                if (
                    isinstance(body_node.func, ast.Attribute)
                    and body_node.func.attr in inefficient_methods
                    and self._is_dataframe(
                        body_node.func.value, dataframe_variables
                    )
                ):
                    return body_node  # Return the inefficient operation node
        return None
