import ast


class LibraryExtractor:
    """
    A utility class for extracting information about libraries and imports
    from Python code represented as an Abstract Syntax Tree (AST).
    """

    def extract_libraries(self, tree: ast.AST) -> list[dict[str, str]]:
        """
        Extracts all libraries imported in the given AST.

        Parameters:
        - tree (ast.AST): The AST of a Python module.

        Returns:
        - list[dict[str, str]]: A list of dictionaries,
          where each dictionary contains:
            - 'name': The name of the library/module.
            - 'alias': The alias of the library/module
              (if present, otherwise None).

        Example:
        ----------
        Code:
            import pandas as pd
            from numpy import array

        Output:
            [
                {'name': 'pandas', 'alias': 'pd'},
                {'name': 'numpy.array', 'alias': None}
            ]
        """
        libraries = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    libraries.append(
                        {"name": alias.name, "alias": alias.asname}
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""  # Handle cases where module is None
                for alias in node.names:
                    full_name = (
                        f"{module}.{alias.name}" if module else alias.name
                    )
                    libraries.append(
                        {"name": full_name, "alias": alias.asname}
                    )
        return libraries

    def get_library_aliases(
        self, libraries: list[dict[str, str]]
    ) -> dict[str, str]:
        """
        Extracts a mapping of library/module names to their aliases.

        Parameters:
        - libraries (list[dict[str, str]]): A list of dictionaries as
          returned by `extract_libraries`.

        Returns:
        - dict[str, str]: A dictionary where:
          - Keys are the full names of the libraries.
          - Values are their aliases
            (or the original name if no alias is used).

        Example:
        ----------
        Input:
            [
                {'name': 'pandas', 'alias': 'pd'},
                {'name': 'numpy.array', 'alias': None}
            ]

        Output:
            {
                'pandas': 'pd',
                'numpy.array': 'numpy.array'
            }
        """
        aliases = {}
        for lib in libraries:
            name = lib["name"]
            alias = (
                lib["alias"] if lib["alias"] else name
            )  # Use name if alias is None
            aliases[name] = alias
        return aliases

    def get_library_of_node(
        self, node: ast.AST, aliases: dict[str, str]
    ) -> str:
        """
        Determines the library associated with a given AST node.

        Parameters:
        - node (ast.AST): The AST node to analyze.
          Typically represents a function or method call.
        - aliases (dict[str, str]): A mapping of library names
          to their aliases (as returned by `get_library_aliases`).

        Returns:
        - str: The library associated with the node, or "Unknown"
          if the library cannot be determined.

        Example:
        ----------
        Code:
            import pandas as pd
            pd.read_csv("file.csv")

        Node:
            <Call AST node for pd.read_csv>

        Output:
            "pandas"

        Notes:
        - This method inspects function calls (`ast.Call`) to determine
          if they belong to a library in `aliases`.
        - For method calls (e.g., `pd.read_csv`), the method checks
          the base object (`pd`) to match it with a library.
        - Returns "Unknown" if the node does not clearly belong to any library.
        """
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):  # e.g., pd.read_csv
                if isinstance(node.func.value, ast.Name):  # e.g., pd
                    base_object = node.func.value.id
                    for library, alias in aliases.items():
                        if alias == base_object:
                            return library
            elif isinstance(
                node.func, ast.Name
            ):  # Direct function calls without attributes
                func_name = node.func.id
                for library, alias in aliases.items():
                    if (
                        alias == func_name
                    ):  # The function name matches a library alias
                        return library
        return "Unknown"
