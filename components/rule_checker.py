import pandas as pd
import ast
from detection_rules.api_specific import (
    chain_indexing_smell,
    dataframe_conversion_api_misused,
    gradients_not_cleared_before_backward_propagation,
    matrix_multiplication_api_misused,
    pytorch_call_method_misused,
    tensor_array_not_used,
)
from detection_rules.generic import (
    broadcasting_feature_not_used,
    columns_and_datatype_not_explicitly_set,
    deterministic_algorithm_option_not_used,
    empty_column_misinitialization,
    hyperparameters_not_explicitly_set,
    in_place_apis_misused,
    memory_not_freed,
    merge_api_parameter_not_explicitly_set,
    nan_equivalence_comparison_misused,
    unnecessary_iteration,
)


class RuleChecker:
    """
    Applies detection rules to Python code using Abstract Syntax Tree (AST)
    analysis.
    """

    def __init__(self, output_path: str):
        """
        Initializes the RuleChecker.

        Parameters:
        - output_path (str): Path where detected smells will be saved.
        """
        self.output_path = output_path
        self._setup_smells()

    def rule_check(
        self,
        ast_node: ast.AST,
        extracted_data: dict[str, any],
        filename: str,
        function_name: str,
        df_output: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Applies all registered smell detectors to the given AST node.

        Parameters:
        - ast_node (ast.AST): The AST node to analyze.
        - extracted_data (dict): Pre-extracted data
        (e.g., libraries, variables, etc.).
        - filename (str): The name of the file being analyzed.
        - function_name (str): The name of the function node being analyzed.
        - df_output (pd.DataFrame): The DataFrame to store detected smells.

        Returns:
        - pd.DataFrame: The updated DataFrame containing detected smells.
        """
        for smell in self.smells:
            try:
                detected_smells = smell.detect(ast_node, extracted_data)
                for detected_smell in detected_smells:
                    df_output.loc[len(df_output)] = {
                        "filename": filename,
                        "function_name": function_name,
                        "smell_name": detected_smell["name"],
                        "line": detected_smell["line"],
                        "description": detected_smell["description"],
                        "additional_info": detected_smell["additional_info"],
                    }
            except Exception as e:
                print(
                    f"Error in rule checker '{type(smell).__name__}' "
                    f"for function '{function_name}' "
                    f"in file '{filename}': {e}"
                )

        return df_output

    def _setup_smells(self) -> None:
        """
        Sets up the smells for the RuleChecker
        by explicitly instantiating them.
        """
        # fmt: off
        self.smells = [
            # API-Specific Smells
            chain_indexing_smell.ChainIndexingSmell(),
            dataframe_conversion_api_misused.DataFrameConversionAPIMisused(),
            gradients_not_cleared_before_backward_propagation.
            GradientsNotClearedSmell(),
            matrix_multiplication_api_misused.MatrixMultiplicationAPIMisused(),
            pytorch_call_method_misused.PyTorchCallMethodMisusedSmell(),
            tensor_array_not_used.TensorArrayNotUsedSmell(),
            # Generic Smells
            broadcasting_feature_not_used.BroadcastingFeatureNotUsedSmell(),
            columns_and_datatype_not_explicitly_set.
            ColumnsAndDatatypeNotExplicitlySetSmell(),
            deterministic_algorithm_option_not_used.
            DeterministicAlgorithmOptionSmell(),
            empty_column_misinitialization.
            EmptyColumnMisinitializationSmell(),
            hyperparameters_not_explicitly_set.
            HyperparametersNotExplicitlySetSmell(),
            in_place_apis_misused.InPlaceAPIsMisusedSmell(),
            memory_not_freed.MemoryNotFreedSmell(),
            merge_api_parameter_not_explicitly_set.
            MergeAPIParameterNotExplicitlySetSmell(),
            nan_equivalence_comparison_misused.
            NanEquivalenceComparisonMisusedSmell(),
            unnecessary_iteration.UnnecessaryIterationSmell(),
        ]
