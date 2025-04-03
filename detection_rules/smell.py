from abc import ABC, abstractmethod
import ast


class Smell(ABC):
    """
    Abstract base class for detecting code smells.
    Provides a standardized interface for smell detection and formatting.
    """

    def __init__(self, name: str, description: str):
        """
        Initializes a Smell instance with its name and description.

        Parameters:
        - name (str): The name of the smell.
        - description (str): A brief description of the smell.
        """
        self.name = name
        self.description = description

    @abstractmethod
    def detect(
        self, ast_node: ast.AST, extracted_data: dict[str, any]
    ) -> list[dict[str, any]]:
        """
        Abstract method to detect code smells.

        This method must be implemented by subclasses and defines
        how the smell is detected
        based on the given AST node and the extracted data.

        Parameters:
        - ast_node (ast.AST): The AST node being analyzed
          (typically the root node of a file or function).
        - extracted_data (dict[str, any]): A dictionary
          containing preprocessed data extracted from the code.

        Structure of `extracted_data`:
        ------------------------------
        - `libraries` (dict[str, str]): Maps library names to their aliases
            (e.g., {"pandas": "pd", "numpy": "np", "tensorflow": "tf"}).
        - `variables` (dict[str, ast.Assign]): Maps variable
            names to their AST assignment nodes.
            Example:
            {
                "df": <Assign AST node>,
                "model": <Assign AST node>
            }
        - `lines` (dict[int, str]): Maps line numbers to
           the corresponding source code.
            Example:
            {
                1: "import pandas as pd",
                2: "df = pd.DataFrame({'a': [1, 2, 3]})"
            }
        - `dataframe_methods` (list[str]): List of Pandas
           methods identified in the code
            (e.g., ["drop", "rename", "merge"]).
        - `dataframe_variables` (list[str]): List of variable
           names identified as Pandas DataFrames.
            Example:
            [
                "df", "data"
            ]
        - `tensor_operations` (list[str]): List of
            tensor operations found in the code
            (e.g., ["dot", "matmul", "transpose"]).
        - `models` (dict[str, dict]): Maps model names to
             their libraries and associated methods.
            Example:
            {
                "model": {
                    "library": "tensorflow",
                    "methods": ["fit", "evaluate"]
                }
            }
        - `model_methods` (dict[str, list[str]]): Maps library
           names to their model-related methods.
            Example:
            {
                "tensorflow": ["fit", "evaluate", "predict"],
                "sklearn": ["fit", "score"]
            }

        Returns:
        - list[dict[str, any]]: A list of dictionaries,
          where each dictionary contains
          information about a detected smell.
        """
        pass

    def format_smell(
        self, line: int, additional_info: str = ""
    ) -> dict[str, any]:
        """
        Formats a detected smell into a standardized dictionary.

        Parameters:
        - line (int): The line number where the smell was detected.
        - additional_info (str): Additional context
          or details about the smell (optional).

        Returns:
        - dict[str, any]: A dictionary containing
          information about the detected smell.
        Example:
        ----------
        {
            "name": "Smell Name",
            "line": 10,
            "description": "This is a code smell description.",
            "additional_info": "Detailed explanation of the smell."
        }
        """
        return {
            "name": self.name,
            "line": line,
            "description": self.description,
            "additional_info": additional_info,
        }
