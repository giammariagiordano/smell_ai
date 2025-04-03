import ast
import pandas as pd


class DataFrameExtractor:
    """
    A utility class for extracting information related to Pandas DataFrames
    from Python code represented as an Abstract Syntax Tree (AST).
    """

    def __init__(self, df_dict_path: str = None):
        """
        Initializes the DataFrameExtractor.

        Parameters:
        - df_dict_path (str): Optional path to the CSV file containing the
          DataFrame method definitions.

        Instance Variables:
        - self.df_methods (list[str]): A list of Pandas DataFrame methods
          loaded from the CSV file.
        """
        self.df_methods = []
        if df_dict_path:
            self.load_dataframe_dict(df_dict_path)

    def load_dataframe_dict(self, path: str):
        """
        Loads a dictionary of Pandas DataFrame methods from a CSV file.

        Parameters:
        - path (str): Path to the CSV file.

        Returns:
        - None: Updates `self.df_methods` with a list of method names.
        """
        df = pd.read_csv(path, dtype={"method": "string"})
        self.df_methods = df["method"].tolist()

    def extract_dataframe_variables(
        self, fun_node: ast.AST, alias: str
    ) -> list[str]:
        """
        Identifies variables initialized as Pandas DataFrames in a function
        or function parameters.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.
        - alias (str): The alias used for Pandas (e.g., "pd").

        Returns:
        - list[str]: A list of variable names identified as DataFrames.
        """
        dataframe_vars = []

        # Include function parameters
        if isinstance(fun_node, ast.FunctionDef):
            for param in getattr(fun_node.args, "args", []):
                if isinstance(param, ast.arg):
                    dataframe_vars.append(param.arg)

        # Include variables assigned as DataFrames
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Assign):

                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    if (
                        isinstance(func, ast.Attribute)
                        and isinstance(func.value, ast.Name)
                        and func.value.id == alias
                        and func.attr == "DataFrame"
                    ):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                dataframe_vars.append(target.id)

            # Derive new DataFrame variables from methods
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    if (
                        isinstance(func, ast.Attribute)
                        and isinstance(func.value, ast.Name)
                        and func.value.id in dataframe_vars
                        and func.attr in self.df_methods
                    ):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                dataframe_vars.append(target.id)

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # If it's an assignment to a variable,
                        # check if it is a DataFrame
                        if isinstance(node.value, ast.Call) and isinstance(
                            node.value.func, ast.Attribute
                        ):
                            if node.value.func.attr in self.df_methods:
                                dataframe_vars.append(target.id)
                        # Check for alias assignment
                        elif (
                            isinstance(node.value, ast.Name)
                            and target.id != node.value.id
                        ):
                            # Handle aliasing of the DataFrame
                            dataframe_vars.append(target.id)
        return list(set(dataframe_vars))

    def track_dataframe_methods(
        self, fun_node: ast.AST, dataframe_vars: list[str]
    ) -> dict[str, list[str]]:
        """
        Tracks methods called on Pandas DataFrames within a function.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.
        - dataframe_vars (list[str]): A list of DataFrame variable names.

        Returns:
        - dict[str, list[str]]: A dictionary
          where keys are DataFrame variable names,
          and values are lists of method names called on those DataFrames.
        """
        methods_usage = {var: [] for var in dataframe_vars}
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Call):  # Look for function/method calls
                func = node.func
                if isinstance(func, ast.Attribute) and isinstance(
                    func.value, ast.Name
                ):
                    if (
                        func.value.id in dataframe_vars
                        and func.attr in self.df_methods
                    ):
                        methods_usage[func.value.id].append(func.attr)
        return methods_usage

    def track_dataframe_accesses(
        self, fun_node: ast.AST, dataframe_vars: list[str]
    ) -> dict[str, list[str]]:
        """
        Tracks column accesses on Pandas DataFrames within a function.

        Parameters:
        - fun_node (ast.AST): The AST node representing a Python function.
        - dataframe_vars (list[str]): A list of DataFrame variable names.

        Returns:
        - dict[str, list[str]]: A dictionary
          where keys are DataFrame variable names,
          and values are lists of column names accessed on those DataFrames.
        """
        accesses = {var: [] for var in dataframe_vars}
        for node in ast.walk(fun_node):
            if isinstance(
                node, ast.Subscript
            ):  # Look for subscript accesses (e.g., df['a'])
                if (
                    isinstance(node.value, ast.Name)
                    and node.value.id in dataframe_vars
                ):
                    if isinstance(
                        node.slice, ast.Constant
                    ):  # Ensure the key is a constant
                        accesses[node.value.id].append(node.slice.value)
        return accesses
