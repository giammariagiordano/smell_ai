import ast
from detection_rules.smell import Smell


class DeterministicAlgorithmOptionSmell(Smell):
    """
    Detects the use of `torch.use_deterministic_algorithms(True)` in PyTorch,
    which may cause performance issues.

    Example of code smell:
        torch.use_deterministic_algorithms(True)
        # Potential performance bottleneck

    Preferred alternative:
        Avoid using this option unless determinism is strictly required.
    """

    def __init__(self):
        super().__init__(
            name="deterministic_algorithm_option_not_used",
            description=(
                "Using `torch.use_deterministic_algorithms(True)` "
                "can cause performance issues. "
                "Avoid using this option unless"
                "determinism is strictly required."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Retrieve libraries and alias mapping
        libraries = extracted_data.get("libraries", {})

        # Traverse AST to detect calls to `use_deterministic_algorithms`
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call):
                # Extract the full function name
                func_name = self._get_full_function_name(node.func, libraries)

                # Match the function name with the target method
                if func_name in [
                    "torch.use_deterministic_algorithms",
                    "use_deterministic_algorithms",
                ]:
                    if (
                        len(node.args) == 1
                        and isinstance(node.args[0], ast.Constant)
                        and node.args[0].value is True
                    ):
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info=(
                                    f"Using `{func_name}(True)` detected."
                                    "Avoid for performance."
                                ),
                            )
                        )

        return smells

    def _get_full_function_name(self, func: ast.AST, libraries: dict) -> str:
        """
        Extracts the full name of a function or method from an AST node,
        handling library aliases.

        Parameters:
        - func: The AST node representing the function or method.
        - libraries: Dictionary of library aliases from extracted_data.

        Returns:
        - str: The full name of the function
          (e.g., "torch.use_deterministic_algorithms").
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
