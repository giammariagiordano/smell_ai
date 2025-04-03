import json
import pandas as pd
from sklearn.model_selection import train_test_split


class DatasetPreparation:
    """
    Class for dataset preparation, including loading, splitting and formatting.
    """

    def __init__(self, input_file, test_size=0.2, random_state=42):
        self.input_file = input_file
        self.test_size = test_size
        self.random_state = random_state

    def load_and_split_dataset(self):
        """
        Load the dataset from a JSON file and split it into
        training and validation sets, using the smell name as the label.
        """
        with open(self.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        samples = []
        for entry in data:

            function_data = entry.get("function_data", {})
            code = function_data.get("code", "")

            if entry.get("smelly", False):
                for smell in entry.get("smells", []):
                    samples.append({
                        "code": code,
                        "label": smell.get("smell_name", "no_smell"),
                        "reason": (
                            f"Description: {smell.get('description', '')}. "
                            f"""Additional Info:
                            {smell.get('additional_info', '')}."""
                        )
                    })
            else:
                samples.append({
                    "code": code,
                    "label": "no_smell",
                    "reason": "No smells detected."
                })

        train_data, val_data = train_test_split(
            samples, test_size=self.test_size, random_state=self.random_state
        )

        return train_data, val_data

    def save_as_csv(
        self, train_data, val_data, train_file="train.csv", val_file="val.csv"
    ):
        """
        Save train and validation datasets as CSV files for further processing.
        """
        pd.DataFrame(train_data).to_csv(train_file, index=False)
        pd.DataFrame(val_data).to_csv(val_file, index=False)
