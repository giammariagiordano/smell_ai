import json
import logging
import os
import concurrent.futures
from data_preparation.code_smell_injector import CodeSmellInjector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class InjectedSmellsDatasetBuilder:
    """
    A class to build a dataset of functions with injected code smells.
    This class processes a dataset of clean functions, injects code smells into
    them using a CodeSmellInjector instance, and saves the results
    incrementally.

    Attributes:
        injector (CodeSmellInjector): An instance of the
            CodeSmellInjector class.
        checkpoint_path (str): Path to the checkpoint
            file to resume processing.
        output_path (str): Path to the output JSON
            file for smelly functions.
        input_path (str): Path to the input JSON file
            containing clean functions.
        timeout_seconds (int): Maximum time allowed
            per function for processing.
    """

    def __init__(
        self,
        injector: CodeSmellInjector,
        checkpoint_path,
        output_path,
        input_path,
        timeout_seconds=1800,
    ):
        """
        Initializes the InjectedSmellsDatasetBuilder.

        Args:
            injector (CodeSmellInjector): An instance of CodeSmellInjector.
            checkpoint_path (str): Path to the checkpoint file.
            output_path (str): Path to the output JSON
                file for smelly functions.
            input_path (str): Path to the input JSON
                file containing clean functions.
            timeout_seconds (int): Maximum time allowed
                per function for processing.
        """
        self.injector = injector
        self.checkpoint_path = checkpoint_path
        self.output_path = output_path
        self.input_path = input_path
        self.timeout_seconds = timeout_seconds

    def load_checkpoint(self):
        """
        Loads the checkpoint and previously processed data if they exist.

        Returns:
            tuple: A tuple containing:
                - checkpoint (dict): A dictionary with
                    the indices of processed functions.
                - smelly_functions (list): A list of
                    already processed smelly functions.
        """
        if os.path.exists(self.checkpoint_path):
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                try:
                    checkpoint = json.load(f)
                except json.JSONDecodeError:
                    logging.warning(
                        f"Checkpoint file {self.checkpoint_path} is "
                        "empty or corrupted. Resetting checkpoint."
                    )
                    checkpoint = {"processed": []}
        else:
            checkpoint = {"processed": []}

        if os.path.exists(self.output_path):
            with open(self.output_path, "r", encoding="utf-8") as f:
                try:
                    smelly_functions = json.load(f)
                except json.JSONDecodeError:
                    logging.warning(
                        f"Output file {self.output_path} is "
                        "empty or corrupted. Starting fresh."
                    )
                    smelly_functions = []
        else:
            smelly_functions = []

        return checkpoint, smelly_functions

    def save_checkpoint(self, processed_indices):
        """
        Saves the checkpoint to a file.

        Args:
            processed_indices (list): List of indices of processed functions.
        """
        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({"processed": processed_indices}, f, indent=4)

    def save_incremental_output(self, smelly_functions):
        """
        Saves the incrementally updated output to the output file.

        Args:
            smelly_functions (list): List of smelly functions processed so far.
        """
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(smelly_functions, f, indent=4)

    def process_function_with_timeout(self, func, index, total_functions):
        """
        Processes a single function with a timeout.

        This method injects code smells into
        a single function and handles any errors
        or timeouts that occur during the process.

        Args:
            func (dict): The function data to process.
            index (int): The index of the function in the dataset.
            total_functions (int): The total number
                of functions in the dataset.

        Returns:
            dict: A dictionary containing the smelly function
                and its labels, or None if processing fails.
        """
        try:
            clean_code = func["code"]
            smelly_function, smells = self.injector.inject_smells(clean_code)

            # Remove Python code block markers if present
            if smelly_function.startswith(
                "python"
            ) and smelly_function.endswith(""):
                smelly_function = smelly_function[9:-3].strip()

            return {
                "code": smelly_function,
                "labels": smells,
            }

        except Exception as e:
            logging.error(
                f"Error processing function {index + 1}/{total_functions}: {e}"
            )
            return None

    def process_dataset(self):
        """
        Processes the dataset by injecting code smells into functions.

        This method reads the input dataset,
            injects code smells into functions,
        and saves the results incrementally.
            It also handles checkpointing to resume
        processing if interrupted.
        """
        with open(self.input_path, "r", encoding="utf-8") as f:
            functions = json.load(f)

        total_functions = len(functions)
        logging.info(
            f"Starting processing {total_functions} "
            "functions from {self.input_path}"
        )

        # Load checkpoint and previously saved output
        checkpoint, smelly_functions = self.load_checkpoint()
        processed_indices = set(checkpoint["processed"])

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            for index, func in enumerate(functions):
                if index in processed_indices:
                    logging.info(
                        f"Skipping function {index + 1}/{total_functions}, "
                        " already processed."
                    )
                    continue

                future = executor.submit(
                    self.process_function_with_timeout,
                    func,
                    index,
                    total_functions,
                )
                try:
                    result = future.result(timeout=self.timeout_seconds)
                    if result:
                        smelly_functions.append(result)
                        logging.info(
                            f"Processed function {index + 1} "
                            f"/{total_functions}: Labels = {result['labels']}"
                        )
                except concurrent.futures.TimeoutError:
                    logging.warning(
                        f"Function {index + 1}/{total_functions} exceeded "
                        f"the timeout of {self.timeout_seconds} seconds. "
                        "Skipping."
                    )

                # Update checkpoint and save incremental output
                processed_indices.add(index)
                self.save_checkpoint(list(processed_indices))
                self.save_incremental_output(smelly_functions)

        logging.info(
            f"Processing complete. Full dataset saved to {self.output_path}"
        )


if __name__ == "__main__":
    from data_preparation.qwen_llm import QwenLLM

    # Initialize the LLM model
    llm_model = QwenLLM()

    # Initialize the CodeSmellInjector
    injector = CodeSmellInjector(llm_model, max_smells=1)

    checkpoint_path = "datasets/output_analysis/checkpoint.json"
    input_path = "datasets/output_analysis/clean_functions.json"
    output_path = "datasets/output_analysis/injected_functions.json"

    # Initialize the InjectedSmellsDatasetBuilder
    dataset_builder = InjectedSmellsDatasetBuilder(
        injector, checkpoint_path, output_path, input_path
    )

    dataset_builder.process_dataset()
