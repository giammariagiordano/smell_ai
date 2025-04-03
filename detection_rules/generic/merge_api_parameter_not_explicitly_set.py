import ast
from detection_rules.smell import Smell


class MergeAPIParameterNotExplicitlySetSmell(Smell):
    """
    Detects cases where Pandas' `merge` API is called
    without explicitly setting important parameters.

    Example of code smell:
        df1.merge(df2)  # Missing 'how', 'on', or 'validate' parameters.

    Preferred alternative:
        df1.merge(df2, how='inner', on='key', validate='one_to_one')
    """

    def __init__(self):
        super().__init__(
            name="merge_api_parameter_not_explicitly_set",
            description=(
                "Calls to Pandas' `merge` API should explicitly set "
                "parameters like 'how', 'on', and 'validate' "
                "to avoid unexpected behavior."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Retrieve library aliases and DataFrame variables
        pandas_alias = extracted_data["libraries"].get("pandas")
        if not pandas_alias:
            return smells

        dataframe_variables = extracted_data.get("dataframe_variables", [])

        # Traverse AST nodes to find calls to `merge`
        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Call)
                and hasattr(node.func, "attr")
                and node.func.attr == "merge"
            ):
                # Resolve the base object calling `merge`
                base_obj = node.func.value

                # Check if `merge` is called on a DataFrame
                # variable or Pandas alias
                is_dataframe_call = (
                    isinstance(base_obj, ast.Name)
                    and base_obj.id in dataframe_variables
                )
                is_pandas_call = (
                    isinstance(base_obj, ast.Attribute)
                    and hasattr(base_obj.value, "id")
                    and base_obj.value.id == pandas_alias
                )

                if is_dataframe_call or is_pandas_call:
                    # Check for missing or incomplete parameters
                    if not hasattr(node, "keywords") or not isinstance(
                        node.keywords, list
                    ):
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info=(
                                    "Missing explicit parameters in `merge` "
                                    "(e.g., 'how', 'on', 'validate')."
                                ),
                            )
                        )
                    else:
                        # Ensure keywords are valid before processing
                        valid_keywords = [
                            kw.arg
                            for kw in node.keywords
                            if isinstance(kw, ast.keyword)
                            and kw.arg is not None
                        ]
                        required_args = {"how", "on", "validate"}
                        if not required_args.issubset(set(valid_keywords)):
                            smells.append(
                                self.format_smell(
                                    line=node.lineno,
                                    additional_info=(
                                        "Incomplete parameters in `merge`. "
                                        "Consider specifying 'how', 'on', "
                                        " and 'validate'."
                                    ),
                                )
                            )

        return smells
