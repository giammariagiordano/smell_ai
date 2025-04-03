import os

from model_training_and_evaluation.dataset_preparation import (
    DatasetPreparation,
)
from model_training_and_evaluation.model import ModelTuner


class Pipeline:
    """
    Main class to integrate DatasetPreparation and Model for fine-tuning
    and using Qwen2.5-Coder-7B-Instruct to detect ML-specific code smells.
    """

    def __init__(
        self,
        dataset_file="./model_training_and_evaluation/dataset.json",
        model_dir="./qwen_code_smell_model",
    ):
        self.dataset_file = dataset_file
        self.model_dir = model_dir
        self.dataset_preparation = DatasetPreparation(input_file=dataset_file)
        self.tuner = ModelTuner()

    def prepare_datasets(self):
        """
        Prepare train and validation datasets from the input file.
        """
        print("Preparing datasets...")
        train_data, val_data = self.dataset_preparation.load_and_split_dataset(
        )
        self.dataset_preparation.save_as_csv(
            train_data, val_data, train_file="train.csv", val_file="val.csv"
        )
        print("Datasets prepared and saved as CSV.")

    def fine_tune_model(self):
        """
        Fine-tune the model using the prepared datasets.
        """
        print("Fine-tuning the model...")
        train_data, val_data = self.tuner.prepare_data("train.csv", "val.csv")
        os.makedirs(self.model_dir, exist_ok=True)
        self.tuner.fine_tune(train_data, val_data, output_dir=self.model_dir)
        print(f"Model fine-tuned and saved to {self.model_dir}.")

    def load_fine_tuned_model(self):
        """
        Load the fine-tuned model from the saved directory.
        """
        if os.path.exists(self.model_dir):
            print("Loading fine-tuned model...")
            self.tuner.load_model(self.model_dir)
            print("Fine-tuned model loaded.")
        else:
            raise FileNotFoundError(
                f"Model directory {self.model_dir} does not exist."
            )

    def detect_code_smell(self, code_snippet):
        """
        Use the fine-tuned model to detect code smells in a given code snippet.
        """
        print("Detecting code smell...")
        if self.tuner is None:
            raise RuntimeError("Model is not loaded.")

        result = self.tuner.detect_code_smell(code_snippet)
        return result

    def run(self):
        """
        Complete workflow: prepare datasets, fine-tune the model,
        and detect code smells.
        """
        # Step 1: Prepare datasets
        self.prepare_datasets()

        # Step 2: Fine-tune the model
        self.fine_tune_model()

        # Step 3: Load the fine-tuned model
        self.load_fine_tuned_model()

        # Step 4: Detect a code smell
        code_snippet = """
        import torch\n

        def gradients_not_cleared():\n
            optimizer = torch.optim.Adam([])\n
            loss = torch.tensor(1.0, requires_grad=True)\n
            loss.backward()\n
            optimizer.step()\n
            return loss",
        """
        result = self.detect_code_smell(code_snippet)
        print("Detected Code Smell:", result)


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run()
