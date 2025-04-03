import ast
from detection_rules.smell import Smell


class ColumnsAndDatatypeNotExplicitlySetSmell(Smell):
    """
    Detects cases where Pandas' DataFrame or read_csv methods are used without
    explicitly specifying column names or datatypes.

    Example of code smell:
        pd.DataFrame(data)  # Missing explicit 'dtype'
        pd.read_csv("file.csv")  # Missing explicit 'dtype'

    Preferred alternative:
        pd.DataFrame(data, dtype="float")  # Specify dtype
        pd.read_csv("file.csv", dtype={"column1": "int", "column2": "float"})
    """

    def __init__(self):
        super().__init__(
            name="columns_and_datatype_not_explicitly_set",
            description=(
                "Pandas' DataFrame or read_csv methods should explicitly"
                "set 'dtype' to avoid unexpected behavior."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Ensure Pandas library is used
        pandas_alias = extracted_data["libraries"].get("pandas")
        if not pandas_alias:
            return smells

        # Traverse AST to find calls to DataFrame or read_csv
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Call)
                and hasattr(node.func, "attr")
                and node.func.attr
                in {"DataFrame", "read_csv"}  # Specific methods to check
                and hasattr(node.func.value, "id")
                and node.func.value.id == pandas_alias
            ):
                # Check for missing or incomplete keyword arguments
                if not hasattr(node, "keywords") or not node.keywords:
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                "Missing explicit 'dtype'"
                                f"in {node.func.attr} call."
                            ),
                        )
                    )
                else:
                    # Check if 'dtype' is explicitly set
                    has_dtype = any(
                        kw.arg == "dtype"
                        for kw in node.keywords
                        if isinstance(kw, ast.keyword)
                    )
                    if not has_dtype:
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info=(
                                    "'dtype' not explicitly set"
                                    f"in {node.func.attr} call."
                                ),
                            )
                        )

        return smells
