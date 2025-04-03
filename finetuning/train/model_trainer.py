from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template


class ModelTrainer:
    """
    A class to handle the loading and configuration of
    a machine learning model, including LoRA optimizations.

    Attributes:
        model_name (str): Name or path of the pretrained model.
        max_seq_length (int): Maximum sequence length for the model.
        dtype (str or None): Data type to use
            (e.g., 'float16', 'bfloat16', None).
        load_in_4bit (bool): Whether to use 4-bit quantization.
        model: The loaded model instance.
        tokenizer: The tokenizer associated with the model.
    """

    def __init__(self, model_name, max_seq_length, dtype, load_in_4bit):
        """
        Initializes the ModelTrainer with the model parameters.

        Args:
            model_name (str): Name or path of the pretrained model.
            max_seq_length (int): Maximum sequence length for the model.
            dtype (str or None): Data type to use
                (e.g., 'float16', 'bfloat16', None).
            load_in_4bit (bool): Whether to use 4-bit quantization.
        """
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.dtype = dtype
        self.load_in_4bit = load_in_4bit
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """
        Loads the pretrained model and
        tokenizer using the specified parameters.
        """
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.model_name,
            max_seq_length=self.max_seq_length,
            dtype=self.dtype,
            load_in_4bit=self.load_in_4bit,
        )

    def apply_lora(
        self,
        r,
        target_modules,
        lora_alpha,
        lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
        use_rslora=False,
        loftq_config=None,
    ):
        """
        Applies LoRA (Low-Rank Adaptation) optimizations to the model.

        Args:
            r (int): Rank of the low-rank matrices used in LoRA.
            target_modules (list[str]): List of module names to apply LoRA.
            lora_alpha (int): Scaling factor for LoRA updates.
            lora_dropout (float): Dropout rate for LoRA updates.
            bias (str): Type of bias to use (default: "none").
            use_gradient_checkpointing (str or bool):
                Whether to use gradient checkpointing (default: "unsloth").
            random_state (int):
                Random seed for reproducibility (default: 3407).
            use_rslora (bool): Whether to use RS-LoRA (default: False).
            loftq_config (dict or None):
                Configuration for LoFTQ quantization (default: None).
        """
        self.model = FastLanguageModel.get_peft_model(
            self.model,
            r=r,
            target_modules=target_modules,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias=bias,
            use_gradient_checkpointing=use_gradient_checkpointing,
            random_state=random_state,
            use_rslora=use_rslora,
            loftq_config=loftq_config,
        )

    def apply_chat_template(self, template_name="qwen-2.5"):
        """
        Applies a chat template to the tokenizer.

        Args:
            template_name (str): The name of the chat template to apply.
                                 Defaults to "qwen-2.5".
        """
        if not self.tokenizer:
            raise ValueError(
                "Tokenizer is not loaded. Call `load_model` first."
            )

        self.tokenizer = get_chat_template(
            self.tokenizer, chat_template=template_name
        )
        print(f"Chat template '{template_name}' applied to the tokenizer.")
