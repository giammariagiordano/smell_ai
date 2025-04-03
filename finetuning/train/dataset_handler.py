import os
import json
from datasets import Dataset


class DatasetHandler:
    def __init__(self, input_path, train_path, val_path, split_dataset=True):
        self.input_path = input_path
        self.train_path = train_path
        self.val_path = val_path
        self.split_dataset = split_dataset

    def load_or_process_dataset(self):
        if not self.split_dataset:
            return self._load_full_train_and_custom_val_dataset()
        if os.path.exists(self.train_path) and os.path.exists(self.val_path):
            return self._load_existing_dataset()
        else:
            return self._process_and_split_dataset()

    def _load_existing_dataset(self):
        with open(self.train_path, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        with open(self.val_path, "r", encoding="utf-8") as f:
            val_data = json.load(f)

        return Dataset.from_dict(train_data), Dataset.from_dict(val_data)

    def _load_full_train_and_custom_val_dataset(self):
        with open(self.input_path, "r", encoding="utf-8") as f:
            train_data = json.load(f)

        train_conversations = [
            [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant trained to "
                        "detect code smells in Python code."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is the code:\n{sample['code']}"
                        "\nIdentify the code smells."
                    ),
                },
                {
                    "role": "assistant",
                    "content": "The code smells are:\n- "
                    + "\n- ".join(sample["labels"]),
                },
            ]
            for sample in train_data
        ]

        train_dataset = Dataset.from_dict(
            {"conversations": train_conversations}
        )

        # Load and combine the two validation files
        with open("datasets/smelly_niche.json", "r", encoding="utf-8") as f:
            smelly_niche_data = json.load(f)
        with open(
            "datasets/output_analysis/smelly_functions.json",
            "r",
            encoding="utf-8",
        ) as f:
            smelly_functions_data = json.load(f)

        combined_val_data = smelly_niche_data + smelly_functions_data

        val_conversations = [
            [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant trained to "
                        "detect code smells in Python code."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is the code:\n{sample['code']}"
                        "\nIdentify the code smells."
                    ),
                },
                {
                    "role": "assistant",
                    "content": "The code smells are:\n- "
                    + "\n- ".join(sample["labels"]),
                },
            ]
            for sample in combined_val_data
        ]

        val_dataset = Dataset.from_dict({"conversations": val_conversations})

        with open(self.train_path, "w", encoding="utf-8") as f:
            json.dump(train_dataset.to_dict(), f)
        with open(self.val_path, "w", encoding="utf-8") as f:
            json.dump(val_dataset.to_dict(), f)

        return train_dataset, val_dataset

    def _process_and_split_dataset(self):
        with open(self.input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        conversations = [
            [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant trained to "
                        "detect code smells in Python code."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is the code:\n{sample['code']}"
                        "\nIdentify the code smells."
                    ),
                },
                {
                    "role": "assistant",
                    "content": "The code smells are:\n- "
                    + "\n- ".join(sample["labels"]),
                },
            ]
            for sample in data
        ]

        dataset = Dataset.from_dict({"conversations": conversations})
        dataset_dict = dataset.train_test_split(
            test_size=0.2, shuffle=True, seed=3407
        )

        with open(self.train_path, "w", encoding="utf-8") as f:
            json.dump(dataset_dict["train"].to_dict(), f)
        with open(self.val_path, "w", encoding="utf-8") as f:
            json.dump(dataset_dict["test"].to_dict(), f)

        return dataset_dict["train"], dataset_dict["test"]

    def format_for_training(self, dataset, tokenizer):
        """
        Formats the dataset using a chat template for training.

        Args:
            dataset (Dataset): The dataset to format.
            tokenizer: The tokenizer used to apply the chat template.

        Returns:
            Dataset: The formatted dataset.
        """
        return dataset.map(
            lambda examples: {
                "text": [
                    tokenizer.apply_chat_template(
                        convo, tokenize=False, add_generation_prompt=False
                    )
                    for convo in examples["conversations"]
                ]
            },
            batched=True,
        )
