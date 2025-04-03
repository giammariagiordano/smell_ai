import argparse

from finetuning.train.model_trainer import ModelTrainer
from finetuning.train.dataset_handler import DatasetHandler
from finetuning.train.training_configuration import TrainingConfiguration


def train_on_mixed_data():
    model_name = "unsloth/Qwen2.5-Coder-3B-Instruct"
    max_seq_length = 2048
    dtype = None
    load_in_4bit = True
    input_path = "datasets/unified_balanced_dataset.json"
    train_path = "datasets/train_dataset.json"
    val_path = "datasets/val_dataset.json"
    output_dir = "finetuning/outputs/mixed"
    epochs = 3
    per_device_batch_size = 8
    gradient_accumulation_steps = 2
    learning_rate = 2e-4
    weight_decay = 0.01
    seed = 42

    print("Loading the model for mixed data...")
    model_trainer = ModelTrainer(
        model_name, max_seq_length, dtype, load_in_4bit
    )  # line too long
    model_trainer.load_model()
    model_trainer.apply_lora(
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0,
    )
    model_trainer.apply_chat_template(template_name="qwen-2.5")

    print("Processing the mixed dataset...")
    dataset_handler = DatasetHandler(input_path, train_path, val_path)
    train_dataset, val_dataset = dataset_handler.load_or_process_dataset()

    print("Formatting the mixed dataset for training...")
    formatted_train_dataset = dataset_handler.format_for_training(
        train_dataset, model_trainer.tokenizer
    )

    print("Configuring the training for mixed data...")
    training_config = TrainingConfiguration(
        model=model_trainer.model,
        tokenizer=model_trainer.tokenizer,
        train_dataset=formatted_train_dataset,
        max_seq_length=max_seq_length,
        output_dir=output_dir,
        epochs=epochs,
        per_device_batch_size=per_device_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
    )
    training_config.configure_training(
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        seed=seed,
    )

    print("Starting training on mixed data...")
    training_config.train_and_save()


def train_on_synthetic_data():
    model_name = "unsloth/Qwen2.5-Coder-3B-Instruct"
    max_seq_length = 2048
    dtype = "None"
    load_in_4bit = True
    input_path = "datasets/injected_only_balanced_dataset.json"
    train_path = "datasets/synthetic_train_dataset.json"
    val_path = "datasets/synthetic_val_dataset.json"
    output_dir = "finetuning/outputs/synthetic"
    epochs = 2.5
    per_device_batch_size = 8
    gradient_accumulation_steps = 2
    learning_rate = 2e-4
    weight_decay = 0.01
    seed = 42

    print("Loading the model for synthetic data...")
    model_trainer = ModelTrainer(
        model_name, max_seq_length, dtype, load_in_4bit
    )  # line too long
    model_trainer.load_model()
    model_trainer.apply_lora(
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0,
    )
    model_trainer.apply_chat_template(template_name="qwen-2.5")

    print("Processing the synthetic dataset...")
    dataset_handler = DatasetHandler(
        input_path, train_path, val_path, split_dataset=False
    )
    train_dataset, _ = dataset_handler.load_or_process_dataset()

    print("Formatting the synthetic dataset for training...")
    formatted_train_dataset = dataset_handler.format_for_training(
        train_dataset, model_trainer.tokenizer
    )

    print("Configuring the training for synthetic data...")
    training_config = TrainingConfiguration(
        model=model_trainer.model,
        tokenizer=model_trainer.tokenizer,
        train_dataset=formatted_train_dataset,
        max_seq_length=max_seq_length,
        output_dir=output_dir,
        epochs=epochs,
        per_device_batch_size=per_device_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
    )
    training_config.configure_training(
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        seed=seed,
    )

    print("Starting training on synthetic data...")
    training_config.train_and_save()


def main():

    parser = argparse.ArgumentParser(
        description="Train a model on mixed or synthetic data."
    )
    parser.add_argument(
        "--mode",
        choices=["mixed", "synthetic"],
        required=True,
        help="Specify the training mode: 'mixed' "
        " for mixed data or 'synthetic' for synthetic data.",
    )
    args = parser.parse_args()

    if args.mode == "mixed":
        train_on_mixed_data()
    elif args.mode == "synthetic":
        train_on_synthetic_data()


if __name__ == "__main__":
    main()
