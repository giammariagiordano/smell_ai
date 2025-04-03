from transformers import TrainingArguments, DataCollatorForSeq2Seq
from trl import SFTTrainer
from unsloth.chat_templates import train_on_responses_only
from unsloth import is_bfloat16_supported


class TrainingConfiguration:
    """
    A class to configure and initialize the training process for a model.

    Attributes:
        trainer (SFTTrainer): The trainer object handling the training process.
        epochs (int): Number of training epochs.
        per_device_batch_size (int): Batch size per device.
        gradient_accumulation_steps (int):
            Number of gradient accumulation steps.
        warmup_percentage (float): Percentage of total steps for warmup.
    """

    def __init__(
        self,
        model,
        tokenizer,
        train_dataset,
        max_seq_length,
        output_dir,
        epochs,
        per_device_batch_size,
        gradient_accumulation_steps,
    ):
        """
        Initializes the TrainingConfiguration with trainer parameters.

        Args:
            model: The pretrained model to be fine-tuned.
            tokenizer: The tokenizer associated with the model.
            train_dataset: The dataset used for training.
            max_seq_length (int): Maximum sequence length for the model.
            output_dir (str): Directory to save the training outputs.
            epochs (int): Number of training epochs.
            per_device_batch_size (int): Batch size per device.
            gradient_accumulation_steps (int):
                Number of gradient accumulation steps.
        """
        self.model = model
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.max_seq_length = max_seq_length
        self.output_dir = output_dir
        self.epochs = epochs
        self.per_device_batch_size = per_device_batch_size
        self.gradient_accumulation_steps = gradient_accumulation_steps

        self.trainer = None
        self.warmup_steps = None

    def calculate_warmup_steps(
        self, dataset_length, epochs, batch_size, warmup_percentage
    ):
        """
        Calculates the number of warmup steps based
        on the dataset length and training parameters.

        Args:
            dataset_length (int): The length of the training dataset.
            epochs (int): Number of training epochs.
            batch_size (int): Batch size per device.
            warmup_percentage (float): Percentage of total steps for warmup.

        Returns:
            int: Number of warmup steps.
        """
        total_steps = dataset_length * epochs // batch_size
        return max(1, int(total_steps * warmup_percentage))

    def configure_training(self, learning_rate, weight_decay, seed):
        """
        Configures and initializes the trainer for training.

        Args:
            learning_rate (float): Learning rate for the optimizer.
            weight_decay (float): Weight decay for regularization.
            seed (int): Random seed for reproducibility.
        """
        batch_size = (
            self.per_device_batch_size * self.gradient_accumulation_steps
        )  # line length

        self.warmup_steps = self.calculate_warmup_steps(
            dataset_length=len(self.train_dataset),
            epochs=self.epochs,
            batch_size=batch_size,
            warmup_percentage=0.05,
        )

        self.trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=self.train_dataset,
            dataset_text_field="text",
            max_seq_length=self.max_seq_length,
            data_collator=DataCollatorForSeq2Seq(tokenizer=self.tokenizer),
            dataset_num_proc=2,
            packing=False,
            args=TrainingArguments(
                per_device_train_batch_size=self.per_device_batch_size,
                gradient_accumulation_steps=self.gradient_accumulation_steps,
                warmup_steps=self.warmup_steps,
                num_train_epochs=self.epochs,
                learning_rate=learning_rate,
                fp16=not is_bfloat16_supported(),
                bf16=is_bfloat16_supported(),
                logging_steps=1,
                eval_strategy="no",
                save_steps=100,
                save_total_limit=3,
                optim="adamw_8bit",
                weight_decay=weight_decay,
                lr_scheduler_type="linear",
                seed=seed,
                output_dir="finetuning/checkpoints",
                report_to="none",
            ),
        )

        # Format training data for responses-only mode
        self.trainer = train_on_responses_only(
            self.trainer,
            instruction_part="<|im_start|>user\n",
            response_part="<|im_start|>assistant\n",
        )

    def train_and_save(self, resume_from_checkpoint=None):
        """
        Executes the training process and saves the final model.

        Args:
            resume_from_checkpoint (str or None):
                Path to a checkpoint to resume training from.
        """

        print("Starting training...")
        print(resume_from_checkpoint)

        if resume_from_checkpoint is not None:
            training_stats = self.trainer.train(
                resume_from_checkpoint=resume_from_checkpoint
            )
        else:
            training_stats = self.trainer.train()

        print(f"Training completed. Stats: {training_stats}")

        # Save the fine-tuned model and tokenizer
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        print(f"Model and tokenizer saved to {self.output_dir}")

        gguf_output_path = f"{self.output_dir}_gguf"
        # Save the model in GGUF format
        self.model.save_pretrained_gguf(
            gguf_output_path,
            tokenizer=self.tokenizer,
            quantization_method="q8_0",
            # or another quantization method like q8_0, f16
        )
        print(f"Model saved in GGUF format at {self.output_dir}")

        # Save the model for Ollama
        ollama_modelfile_path = f"{gguf_output_path}/Modelfile"
        with open(ollama_modelfile_path, "w") as modelfile:
            modelfile.write(self.tokenizer._ollama_modelfile)
        print(f"Model saved for Ollama at {ollama_modelfile_path}")
