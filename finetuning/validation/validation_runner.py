from unsloth import FastLanguageModel
import json

from finetuning.validation.model_inference import ModelInference
from finetuning.validation.dataset_evaluator import DatasetEvaluator


def main():
    # Model configuration
    max_seq_length = 2048
    # Specify the data type (e.g., float16 or bfloat16),
    # or leave as None for auto-detection
    dtype = None
    load_in_4bit = True  # Use 4-bit quantization to save memory

    val_dataset_path = "datasets/synthetic_val_dataset.json"

    # Load the pretrained model and tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="finetuning/outputs/synthetic",
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
    )

    # Optimize the model for inference
    FastLanguageModel.for_inference(model)
    model_inference = ModelInference(model, tokenizer)

    # Define valid labels for evaluation
    valid_labels = {
        "Broadcasting Feature Not Used",
        "Chain Indexing",
        "Columns and DataType Not Explicitly Set",
        "Dataframe Conversion API Misused",
        "Deterministic Algorithm Option Not Used",
        "In-Place APIs Misused",
        "Empty Column Misinitialization",
        "Gradients Not Cleared Before Backward Propagation",
        "Memory Not Freed",
        "Merge API Parameter Not Explicitly Set",
        "NaN Equivalence Comparison Misused",
        "TensorArray Not Used",
        "Randomness Uncontrolled",
        "Hyperparameter Not Explicitly Set",
        "Matrix Multiplication API Misused",
        "PyTorch Call Method Misused",
        "Unnecessary Iteration",
        "No Smell",
    }

    # Load the validation dataset
    with open(val_dataset_path, "r", encoding="utf-8") as f:
        val_data = json.load(f)

    # Initialize the DatasetEvaluator class
    evaluator = DatasetEvaluator(valid_labels)

    # Perform evaluation
    y_true, y_pred = evaluator.evaluate(model_inference, val_data)

    # Calculate metrics (accuracy and classification report)
    accuracy, report = evaluator.calculate_metrics(y_true, y_pred)

    # Print the results
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(report)


if __name__ == "__main__":
    main()
