from collections import defaultdict
import json
import random
import re


class BalancedDatasetBuilder:
    """
    A class to build unified and balanced datasets
    from clean, smelly, and injected functions.

    Attributes:
        clean_path (str): Path to clean functions file.
        smelly_path (str): Path to smelly functions file.
        injected_path (str): Path to injected functions file.
        output_path (str): Path to save the unified dataset.
        label_mapping (dict): Mapping of label
            keys to their human-readable names.
    """

    def __init__(self, clean_path, smelly_path, injected_path, output_path):
        """
        Initializes the BalancedDatasetBuilder.

        Args:
            clean_path (str): Path to clean functions file.
            smelly_path (str): Path to smelly functions file.
            injected_path (str): Path to injected functions file.
            output_path (str): Path to save the unified dataset.
        """
        self.clean_path = clean_path
        self.smelly_path = smelly_path
        self.injected_path = injected_path
        self.output_path = output_path
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

    @staticmethod
    def load_json(file_path):
        """
        Load a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            list: Data loaded from the JSON file.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_json(data, file_path):
        """
        Save data to a JSON file.

        Args:
            data (list): Data to save.
            file_path (str): Path to the JSON file.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def normalize_labels(self, labels):
        """
        Normalize labels using the defined mapping.

        Args:
            labels (list): List of labels to normalize.

        Returns:
            list: Normalized labels.
        """
        return [self.label_mapping.get(label, label) for label in labels]

    @staticmethod
    def extract_python_code(code):
        """
        Extract Python code from a string, handling code blocks.

        Args:
            code (str): The input string potentially containing Python code.

        Returns:
            str: Extracted Python code or the
            original string if no code block is found.
        """
        match = re.search(r"```python\n(.*?)```", code, re.DOTALL)
        if match:
            return match.group(1).strip()
        elif code.startswith("```python"):
            return code[9:].strip()
        else:
            return code.strip()

    @staticmethod
    def remove_comments(code):
        """
        Removes comments from Python code.

        Args:
            code (str): Python code as a string.

        Returns:
            str: Code without comments.
        """
        code_lines = code.splitlines()
        uncommented_lines = [
            line for line in code_lines if not line.strip().startswith("#")
        ]
        return "\n".join(uncommented_lines)

    def process_smelly_functions(self, smelly_functions):
        """
        Process smelly functions by extracting and normalizing labels.

        Args:
            smelly_functions (list): List of smelly functions.

        Returns:
            list: Processed smelly functions.
        """
        processed = [
            {
                "code": func["code"],
                "labels": self.normalize_labels(func["labels"]),
            }
            for func in smelly_functions
        ]
        return processed

    def process_injected_functions(self, injected_functions, max_injected):
        """
        Prepare injected functions by sampling and normalizing labels.

        Args:
            injected_functions (list): List of injected functions.
            max_injected (int): Maximum number
            of injected functions to include.

        Returns:
            list: Processed injected functions.
        """
        sampled = random.sample(
            injected_functions, min(max_injected, len(injected_functions))
        )
        return [
            {
                "code": self.remove_comments(
                    self.extract_python_code(func["code"])
                ),
                "labels": self.normalize_labels(list(set(func["labels"]))),
            }
            for func in sampled
        ]

    def balance_classes(self, smelly, injected, target_per_smell):
        """
        Ensure each smell class is balanced to the target size.

        Args:
            smelly (list): List of smelly functions.
            injected (list): List of injected functions.
            target_per_smell (int): Target number of samples per smell.

        Returns:
            list: Balanced dataset.
        """
        smell_to_samples = defaultdict(list)
        for sample in smelly + injected:
            for label in sample["labels"]:
                smell_to_samples[label].append(sample)

        balanced = []
        for smell, samples in smell_to_samples.items():
            balanced.extend(
                random.sample(samples, min(target_per_smell, len(samples)))
            )

        return balanced

    def build_full_dataset(self, target_clean, target_per_smell, max_injected):
        """
        Build a full unified dataset including smelly and injected functions.

        Args:
            target_clean (int):
                Number of clean samples to include.
            target_per_smell (int):
                Target number of samples per smell.
            max_injected (int):
                Maximum number of injected functions to include.
        """
        # Load datasets
        clean_functions = self.load_json(self.clean_path)
        smelly_functions = self.load_json(self.smelly_path)
        injected_functions = self.load_json(self.injected_path)

        # Process smelly and injected functions
        smelly_processed = self.process_smelly_functions(smelly_functions)
        injected_processed = self.process_injected_functions(
            injected_functions, max_injected
        )

        # Balance classes
        balanced_smells = self.balance_classes(
            smelly_processed, injected_processed, target_per_smell
        )

        # Combine datasets
        final_dataset = clean_functions + balanced_smells
        random.shuffle(final_dataset)

        # Save the dataset
        self.save_json(final_dataset, self.output_path)

        # Calculate and print statistics
        clean_count = len(clean_functions)
        smelly_count = len(smelly_processed)
        injected_count = len(injected_processed)
        total_count = len(final_dataset)
        smell_occurrences = defaultdict(int)
        for sample in balanced_smells:
            for label in sample["labels"]:
                smell_occurrences[label] += 1

        print("Dataset statistics for full dataset:")
        print(f"  Total samples: {total_count}")
        print(f"  Clean samples: {clean_count}")
        print(f"  Smelly samples: {smelly_count}")
        print(f"  Injected samples: {injected_count}")
        print("  Smell occurrences:")
        for smell, count in smell_occurrences.items():
            print(f"    {smell}: {count}")

        print(f"Full dataset saved to {self.output_path}")

    def build_injected_only_dataset(self, max_clean, max_injected):
        """
        Build a dataset including only clean and injected functions.

        Args:
            max_clean (int):
                Maximum number of clean functions to include
            max_injected (int):
                Maximum number of injected functions to include.
        """
        # Load datasets
        clean_functions = self.load_json(self.clean_path)
        injected_functions = self.load_json(self.injected_path)

        # Cap clean functions to max_clean
        clean_functions = clean_functions[:max_clean]

        # Process injected functions
        injected_processed = self.process_injected_functions(
            injected_functions, max_injected
        )

        # Combine datasets
        final_dataset = clean_functions + injected_processed
        random.shuffle(final_dataset)

        # Save the dataset
        output_path = self.output_path.replace("unified", "injected_only")
        self.save_json(final_dataset, output_path)

        # Calculate and print statistics
        clean_count = len(clean_functions)
        injected_count = len(injected_processed)
        total_count = len(final_dataset)

        print("Dataset statistics for injected-only dataset:")
        print(f"  Total samples: {total_count}")
        print(f"  Clean samples: {clean_count}")
        print(f"  Injected samples: {injected_count}")

        print(f"Injected-only dataset saved to {output_path}")


if __name__ == "__main__":
    # Define paths
    clean_path = "datasets/output_analysis/clean_functions.json"
    smelly_path = "datasets/output_analysis/smelly_functions.json"
    injected_path = "datasets/output_analysis/injected_functions.json"
    output_path = "datasets/unified_balanced_dataset.json"

    # Initialize builder
    builder = BalancedDatasetBuilder(
        clean_path, smelly_path, injected_path, output_path
    )

    # Build full dataset including smelly and injected functions
    builder.build_full_dataset(
        target_clean=14000, target_per_smell=700, max_injected=12000
    )

    # Build dataset including only injected functions
    builder.build_injected_only_dataset(max_clean=12000, max_injected=12000)
