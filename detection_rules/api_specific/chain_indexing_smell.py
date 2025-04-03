import ast
from detection_rules.smell import Smell


class ChainIndexingSmell(Smell):
    """
    Detects the use of chained indexing in Pandas DataFrames.

    Example of chained indexing (code smell):
        df["a"][0]  # Can cause performance issues

    Preferred alternative:
        df.loc[0, "a"]  # More explicit and efficient
    """

    def __init__(self):
        super().__init__(
            name="Chain_Indexing",
            description="Using chain indexing may cause performance issues.",
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Ensure the Pandas library is used
        pandas_alias = extracted_data["libraries"].get("pandas")
        if not pandas_alias:
            return smells

        dataframe_variables = extracted_data["dataframe_variables"]

        # Traverse the entire AST
        for node in ast.walk(ast_node):
            # Check if the node is a chained indexing
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Subscript)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id in dataframe_variables
            ):
                smells.append(
                    self.format_smell(
                        line=node.lineno,
                        additional_info="Chained indexing detected in"
                        f"variable '{node.value.value.id}'.",
                    )
                )

        return smells
