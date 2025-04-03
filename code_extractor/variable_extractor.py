import ast


class VariableExtractor:
    """
    A utility class for extracting variable-related information from
    Python code represented as an Abstract Syntax Tree (AST).
    """

    def extract_variable_definitions(
        self, fun_node: ast.AST
    ) -> dict[str, ast.Assign]:
        """
        Extracts variable definitions and their
        associated AST nodes from a function node.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.

        Returns:
        - dict[str, ast.Assign]: A dictionary where keys
          are variable names and values are the corresponding
          AST nodes for their definitions.
        """
        definitions = {}
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Assign):  # Look for assignment statements
                for target in node.targets:  # Variables being assigned to
                    if isinstance(
                        target, ast.Name
                    ):  # Ensure it's a simple variable
                        definitions[target.id] = (
                            node  # Map variable name to its AST node
                        )
        return definitions

    def track_variable_usage(
        self, fun_node: ast.AST
    ) -> dict[str, list[ast.Name]]:
        """
        Tracks the usage of variables in a function
        node and associates them with AST nodes.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.

        Returns:
        - dict[str, list[ast.Name]]: A dictionary where keys
          are variable names and values are lists of AST nodes
          representing their usage.

        Example:
        ----------
        Code:
            def example():
                x = 10
                y = x + 5
                print(y)

        Output:
            {
                'x': [<Name AST node at line 3>],
                'y': [<Name AST node at line 4>]
            }
        """
        usage = {}
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Name):  # Look for variable references
                var_name = node.id
                if var_name not in usage:
                    usage[var_name] = (
                        []
                    )  # Initialize the list if not already present
                usage[var_name].append(node)  # Store the AST node itself
        return usage
