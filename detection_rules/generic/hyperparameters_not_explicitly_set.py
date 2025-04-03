import ast
from detection_rules.smell import Smell


class HyperparametersNotExplicitlySetSmell(Smell):
    """
    Detects cases where hyperparameters are not
    explicitly set when defining models.

    Example of code smell:
        model = Model()  # No hyperparameters set

    Preferred alternative:
        model = Model(hyperparameter=value)  # Explicitly set hyperparameters
    """

    def __init__(self):
        super().__init__(
            name="hyperparameters_not_explicitly_set",
            description=(
                "Hyperparameters should be explicitly set when defining "
                "models to ensure clarity and reproducibility."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Retrieve model methods and libraries
        model_methods = extracted_data.get("model_methods", [])
        libraries = extracted_data.get("libraries", {})

        if not libraries:
            return smells

        # Normalize model method names (remove '()' if present)
        normalized_model_methods = [
            method.replace("()", "") for method in model_methods
        ]

        # Traverse AST to find calls to model definitions
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call):
                # Extract the full function name
                func_name = self._get_full_function_name(node.func, libraries)

                # Match the function name with normalized methods
                base_func_name = func_name.split(".")[-1]
                if base_func_name in normalized_model_methods:
                    if not node.args and not getattr(node, "keywords", None):
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info=(
                                    f"Hyperparameters not explicitly "
                                    f"set for model '{func_name}'. "
                                    "Consider defining key "
                                    "hyperparameters for clarity."
                                ),
                            )
                        )

        return smells

    def _get_full_function_name(self, func: ast.AST, libraries: dict) -> str:
        """
        Extracts the full name of a function or method from
        an AST node, handling library aliases.

        Parameters:
        - func: The AST node representing the function or method.
        - libraries: Dictionary of library aliases from extracted_data.

        Returns:
        - str: The full name of the function
          (e.g., "sklearn.ensemble.RandomForestClassifier").
        """
        names = []
        while isinstance(func, ast.Attribute):
            names.append(func.attr)
            func = func.value

        if isinstance(func, ast.Name):
            # Handle aliases for libraries
            if func.id in libraries.values():
                alias = next(
                    key for key, value in libraries.items() if value == func.id
                )
                names.append(alias)
            else:
                names.append(func.id)
        return ".".join(reversed(names))
