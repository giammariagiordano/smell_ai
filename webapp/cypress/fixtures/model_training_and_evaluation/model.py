import os
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from datasets import Dataset
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)


class Model:
    """
    Class for fine-tuning Qwen2.5-Coder-7B-Instruct
    for ML-specific code smell detection.
    """

    def __init__(self, model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
        )

        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        self.label2id = {}
        self.id2label = {}

    def load_fine_tuned_model(
        self, model_dir: str = "./model_training_and_evaluation/qwen"
    ):
        """
        Load the fine-tuned model and tokenizer from a directory.
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError("Model directory does not exist")

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype="auto",
            device_map="auto",
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
        )
        print(f"Fine-tuned model successfully loaded from {model_dir}.")

    def prepare_data(self, train_file: str, val_file: str):
        """
        Load and tokenize datasets for training and evaluation.
        """
        if not os.path.exists(train_file):
            raise FileNotFoundError(f"Training file not found: {train_file}")
        if not os.path.exists(val_file):
            raise FileNotFoundError(f"Validation file not found: {val_file}")

        train_data = Dataset.from_csv(train_file)
        val_data = Dataset.from_csv(val_file)

        if (
            "code" not in train_data.column_names
            or "label" not in train_data.column_names
            or "reason" not in train_data.column_names
        ):
            raise ValueError(
                "The dataset must contain 'code', 'label' and 'reason columns."
            )

        labels = train_data.unique("label")
        self.label2id = {label: i for i, label in enumerate(labels)}
        self.id2label = {i: label for label, i in self.label2id.items()}

        def apply_chat_format(function):
            messages = [
                {
                    "role": "system",
                    "content": """You are Qwen, a helpful coding assistant
                    trained by Alibaba Cloud. Help improve and refactor
                    Python code efficiently.
                    Analyze the provided code step-by-step
                    to infer the code smell.""",
                },
                {
                    "role": "user",
                    "content": f"""Code:
                    {function["code"]}

                    Question:
                    What is wrong with this code? Please explain step-by-step
                    before providing a label.""",
                },
                {
                    "role": "assistant",
                    "content": f"""Reason: {function["reason"]}
                    Label: {function["label"]}""",
                },
            ]

            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False)
            function["input_ids"] = self.tokenizer(
                text, max_length=512, truncation=True, padding="max_length"
            )["input_ids"]
            function["label"] = self.label2id[function["label"]]
            return function

        train_data = train_data.map(apply_chat_format, batched=True)
        val_data = val_data.map(apply_chat_format, batched=True)

        return train_data, val_data

    def compute_metrics(self, eval_pred):
        """
        Compute evaluation metrics using scikit-learn.
        """
        logits, labels = eval_pred
        predictions = logits.argmax(axis=-1)

        accuracy = accuracy_score(labels, predictions)
        precision = precision_score(labels, predictions, average="weighted")
        recall = recall_score(labels, predictions, average="weighted")
        f1 = f1_score(labels, predictions, average="weighted")

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    def fine_tune(
        self,
        train_data,
        val_data,
        output_dir: str = "./model_training_and_evaluation/qwen",
        hyperparameters: dict = None,
    ):
        """
        Fine-tune the Qwen model.
        """
        if self.model is None:
            raise RuntimeError(
                "Model is not loaded. Load the model before fine-tuning."
            )

        if hyperparameters is None:
            hyperparameters = {
                "learning_rate": 2e-5,
                "batch_size": 16,
                "num_epochs": 3,
                "weight_decay": 0.01,
            }

        training_args = TrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="epoch",
            learning_rate=hyperparameters["learning_rate"],
            per_device_train_batch_size=hyperparameters["batch_size"],
            num_train_epochs=hyperparameters["num_epochs"],
            weight_decay=hyperparameters["weight_decay"],
            save_total_limit=2,
            load_best_model_at_end=True,
            logging_dir="./logs",
            logging_steps=10,
        )

        train_data = train_data.map(
            lambda x: {"input_ids": x["input_ids"], "label": x["label"]}
        )
        val_data = val_data.map(
            lambda x: {"input_ids": x["input_ids"], "label": x["label"]}
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_data,
            eval_dataset=val_data,
            tokenizer=self.tokenizer,
            compute_metrics=self.compute_metrics,
        )

        trainer.train()

        # Save the fine-tuned model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

    def detect_code_smell(
        self, code_snippet: str,
        max_new_tokens: int = 512,
        temperature: float = 0.6
    ):
        """
        Use the model to detect code smells in a code snippet
        using Chain-of-Thought (CoT) reasoning.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        # Chain-of-Thought Prompt
        messages = [
            {
                "role": "system",
                "content": """You are Qwen, a helpful coding assistant trained
                by Alibaba Cloud. Help improve and
                refactor Python code efficiently.
                Analyze the provided code step-by-step
                to infer the code smell.""",
            },
            {
                "role": "user",
                "content": f"""Code:
                {code_snippet}

                Question:
                What is wrong with this code? Please explain step-by-step
                before providing a label.""",
            },
        ]

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer(
            [text], return_tensors="pt"
            ).to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            repetition_penalty=1.0,
        )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(
                model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True)[0]

        return response
