import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from components.inspector import Inspector


class CodeSmellAnalyzer:
    """
    Class to analyze code smells in functions extracted from a dataset.
    """

    def __init__(
        self, dataset_path, output_dir, max_workers=4, log_interval=100
    ):
        """
        Initialize the analyzer with the dataset path and output directory.

        Args:
            dataset_path (str): Path to the dataset JSON file.
            output_dir (str): Directory to save results.
            max_workers (int): Maximum number of threads for parallelization.
            log_interval (int): Number of functions
            to process before logging progress.
        """
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.log_interval = log_interval

        os.makedirs(output_dir, exist_ok=True)
        self.inspector = Inspector(output_path=output_dir)
        self.smelly_results = []
        self.clean_results = []
        self.file_cache = {}

        # Mapping for normalizing smell labels
        self.label_mapping = {
            "hyperparameters_not_explicitly_set": (
                "Hyperparameter Not Explicitly Set"
            ),
            "pytorch_call_method_misused": ("PyTorch Call Method Misused"),
            "gradients_not_cleared_before_backward_propagation": (
                "Gradients Not Cleared Before Backward Propagation"
            ),
            "matrix_multiplication_api_misused": (
                "Matrix Multiplication API Misused"
            ),
            "dataframe_conversion_api_misused": (
                "Dataframe Conversion API Misused"
            ),
            "columns_and_datatype_not_explicitly_set": (
                "Columns and DataType Not Explicitly Set"
            ),
            "in_place_apis_misused": ("In-Place APIs Misused"),
            "unnecessary_iteration": ("Unnecessary Iteration"),
            "empty_column_misinitialization": (
                "Empty Column Misinitialization"
            ),
            "chain_indexing": ("Chain Indexing"),
            "nan_equivalence_comparison_misused": (
                "NaN Equivalence Comparison Misused"
            ),
            "deterministic_algorithm_option_not_used": (
                "Deterministic Algorithm Option Not Used"
            ),
            "randomness_uncontrolled": ("Randomness Uncontrolled"),
            "merge_api_parameter_not_explicitly_set": (
                "Merge API Parameter Not Explicitly Set"
            ),
            "memory_not_freed": ("Memory Not Freed"),
            "tensorarray_not_used": ("TensorArray Not Used"),
            "broadcasting_feature_not_used": ("Broadcasting Feature Not Used"),
            "Chain_Indexing": ("Chain Indexing"),
            "Pytorch Call Method Misused": ("PyTorch Call Method Misused"),
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def load_dataset(self):
        """
        Load the dataset from the JSON file.
        """
        with open(self.dataset_path, "r") as f:
            self.dataset = json.load(f)

    def analyze_function_in_file(self, function_data):
        """
        Analyze a function by analyzing the entire file and filtering results.

        Args:
            function_data (dict):
                Function data containing file_path, function_name, and code.

        Returns:
            dict: Result indicating if the function is smelly and its smells.
        """
        file_path = function_data["file_path"]

        # Use cache if the file has already been inspected
        if file_path not in self.file_cache:
            try:
                self.file_cache[file_path] = self.inspector.inspect(file_path)
            except Exception as e:
                self.logger.error(f"Error analyzing file {file_path}: {e}")
                return None

        results = self.file_cache[file_path]
        function_smells = results[
            (results["function_name"] == function_data["function_name"])
        ]

        if not function_smells.empty:
            # Consolidate all smells for the function
            raw_labels = list(
                set(
                    item["smell_name"]
                    for item in function_smells.to_dict(orient="records")
                )
            )
            # Apply the mapping to normalize labels
            normalized_labels = [
                (
                    self.label_mapping[label]
                    if label in self.label_mapping
                    else label
                )
                for label in raw_labels
            ]
            return {
                "code": function_data["code"],
                "labels": normalized_labels,
            }
        else:
            return {
                "code": function_data["code"],
                "labels": ["No Smell"],
            }

    def analyze_dataset_parallel(self):
        """
        Analyze the entire dataset of functions in parallel.
        """
        self.load_dataset()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_function = {
                executor.submit(
                    self.analyze_function_in_file, function_data
                ): function_data
                for function_data in self.dataset
            }

            for i, future in enumerate(
                as_completed(future_to_function), start=1
            ):
                function_data = future_to_function[future]
                try:
                    result = future.result()
                    if result is not None:
                        if "No Smell" in result["labels"]:
                            self.clean_results.append(result)
                        else:
                            self.smelly_results.append(result)
                except Exception as e:
                    self.logger.error(
                        "Error analyzing function "
                        f"{function_data['function_name']} "
                        f"in file {function_data['file_path']}: {e}"
                    )

                # Log progress
                if i % self.log_interval == 0 or i == len(self.dataset):
                    self.logger.info(
                        f"Processed {i}/{len(self.dataset)} functions..."
                    )

    def save_results(self):
        """
        Save clean and smelly functions to JSON files.
        """
        clean_path = os.path.join(self.output_dir, "clean_functions.json")
        smelly_path = os.path.join(self.output_dir, "smelly_functions.json")

        # Save clean functions
        with open(clean_path, "w", encoding="utf-8") as f:
            json.dump(self.clean_results, f, indent=4)

        # Save smelly functions
        with open(smelly_path, "w", encoding="utf-8") as f:
            json.dump(self.smelly_results, f, indent=4)

        self.logger.info(f"Results saved: {clean_path}, {smelly_path}")

    def run(self):
        """
        Run the analysis process.
        """
        self.logger.info("Starting dataset analysis...")
        self.analyze_dataset_parallel()
        self.save_results()
        self.logger.info(
            f"Analysis completed. Clean functions: {len(self.clean_results)}, "
            f"Smelly functions: {len(self.smelly_results)}"
        )


if __name__ == "__main__":
    dataset_path = "datasets/function_extracted.json"
    output_dir = "datasets/output_analysis"

    analyzer = CodeSmellAnalyzer(dataset_path, output_dir, max_workers=16)
    analyzer.run()
