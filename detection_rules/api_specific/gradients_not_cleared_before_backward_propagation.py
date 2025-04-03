import ast
from detection_rules.smell import Smell


class GradientsNotClearedSmell(Smell):
    """
    Detects cases where gradients are not cleared
    before backward propagation in PyTorch.

    Example of code smell:
        optimizer.backward()  # Missing zero_grad() before backward()

    Preferred alternative:
        optimizer.zero_grad()
        optimizer.backward()  # Proper sequence
    """

    def __init__(self):
        super().__init__(
            name="gradients_not_cleared_before_backward_propagation",
            description=(
                "radients must be cleared using `zero_grad()`"
                " before calling `backward()`."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:

        smells = []

        # Ensure the Torch library is used
        torch_alias = extracted_data["libraries"].get("torch")
        if not torch_alias:
            return smells

        lines = extracted_data.get("lines", {})

        variables = extracted_data["variables"]

        # Traverse the AST to detect improper usage of gradients
        for node in ast.walk(ast_node):
            if isinstance(
                node, (ast.For, ast.While)
            ):  # Look for loops (for/while)
                zero_grad_called = False

                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call) and isinstance(
                        subnode.func, ast.Attribute
                    ):
                        # Detect `zero_grad` calls
                        if (
                            subnode.func.attr == "zero_grad"
                            and isinstance(subnode.func.value, ast.Name)
                            and subnode.func.value.id in variables
                        ):
                            zero_grad_called = True

                        # Detect `backward` calls
                        if (
                            subnode.func.attr == "backward"
                            and isinstance(subnode.func.value, ast.Name)
                            and subnode.func.value.id
                            in extracted_data["variables"]
                            and not zero_grad_called
                        ):
                            # Extract the offending line for additional context
                            code_snippet = lines.get(
                                subnode.lineno, "<Code not available>"
                            )
                            smells.append(
                                self.format_smell(
                                    line=subnode.lineno,
                                    additional_info=(
                                        f"`zero_grad()` not called before"
                                        " `backward()` in loop. "
                                        f"Code: {code_snippet}"
                                    ),
                                )
                            )
        return smells
