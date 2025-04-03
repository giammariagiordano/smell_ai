import ast
from detection_rules.smell import Smell


class MemoryNotFreedSmell(Smell):
    """
    Detects cases where memory is not freed in TensorFlow,
    such as not calling tf.keras.backend.clear_session()
    inside loops where models are defined.

    Example of code smell:
        for i in range(10):
            model = build_model()  # Define model in a loop
            # Missing tf.keras.backend.clear_session()

    Preferred alternative:
        for i in range(10):
            model = build_model()
            tf.keras.backend.clear_session()  # Free memory explicitly
    """

    def __init__(self):
        super().__init__(
            name="memory_not_freed",
            description=(
                "Memory not freed after model definition "
                "in loops may lead to memory leakage. "
                "Consider using tf.keras.backend.clear_session() "
                "to free memory explicitly."
            ),
        )

    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:
        smells = []

        # Ensure TensorFlow is imported
        tensorflow_alias = extracted_data["libraries"].get("tensorflow")
        if not tensorflow_alias:
            return smells

        model_methods = ["Sequential", "Model"]

        # Identify loops in the AST
        loop_nodes = [
            node
            for node in ast.walk(ast_node)
            if isinstance(node, (ast.For, ast.While))
        ]

        for loop_node in loop_nodes:

            # Check if a model is defined in the loop
            model_defined = self._is_model_defined_in_loop(
                loop_node, tensorflow_alias, model_methods
            )

            # Check if memory is freed with clear_session
            memory_freed = self._is_memory_freed_in_loop(
                loop_node, tensorflow_alias
            )

            # If model is defined but memory is not freed, report it
            if model_defined and not memory_freed:
                smells.append(
                    self.format_smell(
                        line=loop_node.lineno,
                        additional_info=(
                            "Memory not freed after model definition in loop. "
                            "Consider using tf.keras.backend.clear_session()."
                        ),
                    )
                )
        return smells

    def _is_model_defined_in_loop(
        self,
        loop_node: ast.AST,
        tensorflow_alias: str,
        model_methods: list[str],
    ) -> bool:
        """
        Check if any model is being defined inside a loop using any of the
        model methods.
        """
        for node in ast.walk(loop_node):
            if isinstance(node, ast.Call):
                # Iterate over all possible model methods
                # (e.g., Sequential, Model, etc.)
                for method in model_methods:
                    if self._is_nested_call(
                        node, tensorflow_alias, ["keras", method]
                    ):
                        return True
        return False

    def _is_memory_freed_in_loop(
        self, loop_node: ast.AST, tensorflow_alias: str
    ) -> bool:
        """
        Check if memory is cleared using tf.keras.backend.clear_session()
        inside a loop.
        """
        for node in ast.walk(loop_node):
            if isinstance(node, ast.Call):
                if self._is_nested_call(
                    node,
                    tensorflow_alias,
                    ["keras", "backend", "clear_session"],
                ):
                    return True
        return False

    def _is_nested_call(
        self, node: ast.Call, base: str, attributes: list[str]
    ) -> bool:
        """
        Checks if the call matches a nested attribute chain
        (e.g., tf.keras.Sequential()).

        Parameters:
        - node: The AST node to check.
        - base: The base alias (e.g., "tf").
        - attributes: List of attributes to match in order
          (e.g., ["keras", "Sequential"]).

        Returns:
        - True if the call matches the nested attribute chain, False otherwise.
        """
        current = node.func
        for attr in reversed(attributes):
            if not isinstance(current, ast.Attribute) or current.attr != attr:
                return False
            current = current.value  # Move to the next level

        # Check if the final level is the expected base (e.g., tf)
        if isinstance(current, ast.Name) and current.id == base:
            return True
        return False
