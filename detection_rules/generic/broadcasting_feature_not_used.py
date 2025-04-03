import ast
from detection_rules.smell import Smell


class BroadcastingFeatureNotUsedSmell(Smell):
    """
    Detects cases where TensorFlow's broadcasting feature is not used,
    and tiling is applied unnecessarily.

    Example of code smell:
        tensor_a = tf.constant([[1], [2], [3]])
        tensor_b = tf.constant([1, 2, 3])
        tensor_c = tf.tile(tensor_a, [1, 3]) + tensor_b  # Inefficient tiling

    Preferred alternative:
        Use broadcasting:
        tensor_a = tf.constant([[1], [2], [3]])
        tensor_b = tf.constant([1, 2, 3])
        tensor_c = tensor_a + tensor_b  # Broadcasting applied
    """

    def __init__(self):
        super().__init__(
            name="Broadcasting_Feature_Not_Used",
            description=(
                "Using broadcasting in TensorFlow is preferred over "
                "tiling arrays unnecessarily. "
                "Broadcasting allows arithmetic between arrays of "
                "different shapes, saving memory and computation time."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:
        smells = []

        # Check for TensorFlow library
        tensorflow_alias = extracted_data["libraries"].get("tensorflow", None)
        if not tensorflow_alias:
            return smells

        # Identify variables created by tf.tile
        tiled_variables = self._tensor_check_tiling(ast_node, tensorflow_alias)

        # Check for arithmetic operations involving tiled variables
        smells.extend(self._check_broadcasting(ast_node, tiled_variables))

        return smells

    def _tensor_check_tiling(
        self, fun_node: ast.AST, tensorflow_alias: str
    ) -> dict:
        """
        Identifies tensor variables that have undergone tiling operations.

        :param fun_node: The AST node representing the function.
        :param tensorflow_alias: Alias used for
               TensorFlow in the code (e.g., "tf").
        :return: Dictionary mapping tiled variable names to their AST nodes.
        """
        tiled_variables = {}
        for node in ast.walk(fun_node):
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "tile"
                and getattr(node.value.func.value, "id", None)
                == tensorflow_alias
            ):
                if isinstance(node.targets[0], ast.Name):
                    tiled_variables[node.targets[0].id] = node
        return tiled_variables

    def _check_broadcasting(
        self, fun_node: ast.AST, tiled_variables: dict
    ) -> list[dict]:
        smells = []
        for node in ast.walk(fun_node):
            if isinstance(
                node, ast.BinOp
            ):  # Arithmetic operation (e.g., +, -, *, /)
                # Check for tiled variables
                if (
                    isinstance(node.left, ast.Name)
                    and node.left.id in tiled_variables
                ) or (
                    isinstance(node.right, ast.Name)
                    and node.right.id in tiled_variables
                ):
                    variable_name = (
                        node.left.id
                        if isinstance(node.left, ast.Name)
                        else node.right.id
                    )
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                f"Variable '{variable_name}' involves "
                                "unnecessary tiling. "
                                "Consider using broadcasting instead."
                            ),
                        )
                    )
                # Check for inline tf.tile calls
                elif (
                    isinstance(node.left, ast.Call)
                    and self._is_tile_call(node.left)
                ) or (
                    isinstance(node.right, ast.Call)
                    and self._is_tile_call(node.right)
                ):
                    smells.append(
                        self.format_smell(
                            line=node.lineno,
                            additional_info=(
                                "Inline use of `tf.tile` detected. "
                                "Consider using broadcasting instead."
                            ),
                        )
                    )
        return smells

    def _is_tile_call(self, node: ast.Call) -> bool:
        """
        Check if the given AST node represents a call to `tf.tile`.
        """
        return (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "tile"
            and getattr(node.func.value, "id", None) == "tf"
        )
