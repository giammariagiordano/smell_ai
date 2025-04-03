import ast
from detection_rules.smell import Smell


class PyTorchCallMethodMisusedSmell(Smell):
    """
    Detects misuse of the `forward` method in PyTorch models.

    Example of code smell:
        self.forward(x)  # Direct call to forward() is discouraged.

    Preferred alternative:
        self.net(x)  # Use the model's instance directly.
    """

    def __init__(self):
        super().__init__(
            name="pytorch_call_method_misused",
            description=(
                "Direct calls to `forward` in PyTorch models are discouraged. "
                "Use the model instance directly instead."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:
        smells = []

        # Find all aliases associated with PyTorch
        torch_aliases = extracted_data["libraries"].get("torch")
        if not torch_aliases:
            return smells

        variable_names = set(extracted_data["variables"].keys())

        for node in ast.walk(ast_node):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "forward"
            ):
                base_name = self._get_base_name(node.func.value)

                # Case 1: Call on `self`
                if base_name == "self":
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                "Direct call to `self.forward()` detected. "
                                "Use the model instance directly instead."
                            ),
                        )
                    )
                # Case 2: Call on a variable associated with PyTorch models
                elif base_name in variable_names:
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                f"Direct call to `{base_name}.forward()` "
                                "detected. Use the model instance "
                                "directly instead."
                            ),
                        )
                    )
        return smells

    def _get_base_name(self, node):
        """
        Recursively finds the base name for an `ast.Attribute` node.

        Parameters:
        - node (ast.AST): The node to analyze.

        Returns:
        - str: The base name if found, otherwise None.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_base_name(node.value)
        return None
