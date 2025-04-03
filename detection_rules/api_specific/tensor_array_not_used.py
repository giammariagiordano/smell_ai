import ast
from detection_rules.smell import Smell


class TensorArrayNotUsedSmell(Smell):
    """
    Detects the misuse of `tf.constant()` in loops
    instead of `tf.TensorArray` in TensorFlow.
    """

    def __init__(self):
        super().__init__(
            name="tensor_array_not_used",
            description=(
                "If `tf.constant()` is used to initialize an array and"
                " modified in a loop, it may cause errors. "
                "Consider using `tf.TensorArray`"
                "for dynamically growing arrays."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:
        smells = []

        # Check for TensorFlow library alias
        tensorflow_alias = extracted_data["libraries"].get("tensorflow")
        if not tensorflow_alias:
            return smells

        # Track tensor variables initialized with `tf.constant`
        tensor_constants = set()
        # First Pass: Detect `tf.constant` assignments and track the variable
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Assign) and isinstance(
                node.value, ast.Call
            ):
                if (
                    hasattr(node.value.func, "attr")
                    and node.value.func.attr == "constant"
                    and hasattr(node.value.func.value, "id")
                    and node.value.func.value.id == tensorflow_alias
                ):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            tensor_constants.add(target.id)

        # Second Pass: Check if the tracked tensor is modified inside a loop
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Assign) and isinstance(
                node.value, ast.Call
            ):
                # Detect `tf.concat` calls
                if (
                    hasattr(node.value.func, "attr")
                    and node.value.func.attr == "concat"
                    and hasattr(node.value.func.value, "id")
                    and node.value.func.value.id == tensorflow_alias
                ):

                    # Extract the tensor names from `tf.concat` arguments
                    concat_arguments = self._extract_tensor_names_from_concat(
                        node.value
                    )

                    # Filter out the constants that
                    # are being modified by `tf.concat`
                    modified_tensors = [
                        var
                        for var in concat_arguments
                        if var in tensor_constants
                    ]

                    # Smell is only valid if inside a loop
                    if modified_tensors and self._is_in_loop(node, ast_node):
                        smells.append(
                            self.format_smell(
                                line=node.lineno,
                                additional_info=(
                                    "Using `tf.TensorArray` is better"
                                    " for dynamically growing arrays."
                                ),
                            )
                        )

        return smells

    def _extract_tensor_names_from_concat(self, node: ast.Call) -> list[str]:
        """
        Extracts tensor names from the arguments of a `tf.concat` call.
        This function handles nested structures
        like lists and other function calls.
        """
        tensor_names = []
        for arg in node.args:
            if isinstance(arg, ast.Name):
                tensor_names.append(arg.id)
            elif isinstance(arg, ast.List):
                # Handle lists inside the `concat` argument
                for item in arg.elts:
                    if isinstance(item, ast.Name):
                        tensor_names.append(item.id)
                    elif isinstance(item, ast.Call):
                        # Handle function calls
                        # (e.g., tensor in function calls inside the list)
                        tensor_names.append(
                            self._extract_tensor_name_from_call(item)
                        )
        return tensor_names

    def _extract_tensor_name_from_call(self, node: ast.Call) -> str:
        """
        Extracts tensor names from function calls
        in the arguments (e.g., `tf.some_function(x)`).
        """
        if isinstance(node.func, ast.Name):
            return node.func.id
        return ""

    def _is_in_loop(self, node: ast.AST, root_node: ast.AST) -> bool:
        current = node
        while current:
            parent = self._find_parent_node(current, root_node)
            if isinstance(
                parent, (ast.For, ast.While)
            ):  # Ensure loop is recognized

                return True
            current = parent
        return False

    def _find_parent_node(self, node: ast.AST, root_node: ast.AST) -> ast.AST:
        """
        Finds the parent node of a given node within the AST.
        """
        for parent in ast.walk(root_node):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    return parent
        return None
