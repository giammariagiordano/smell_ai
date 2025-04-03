import numpy as np
from sklearn.metrics import classification_report  # type: ignore

from finetuning.validation.smell_parser import SmellParser


class DatasetEvaluator:
    """
    A class for evaluating a model's performance on a validation dataset.

    Attributes:
        valid_labels (set): A set of valid code
                            smell labels to validate predictions.
    """

    def __init__(self, valid_labels):
        """
        Initializes the DatasetEvaluator class.

        Args:
            valid_labels (set): A set of valid labels
                                to validate predictions against.
        """
        self.valid_labels = valid_labels

    def evaluate(self, model_inference, val_data):
        """
        Evaluates the model on the validation dataset.

        This method compares the model's predicted labels with the ground truth
        labels for each conversation in the validation dataset.

        Args:
            model_inference (ModelInference):
                An instance of the ModelInference class
                to perform inference.
            val_data (dict):
                A dictionary containing the validation dataset, with
                "conversations" as the key for a list of conversations.

        Returns:
            tuple: Two lists -
                - y_true (list): Ground truth labels for each conversation.
                - y_pred (list): Predicted labels for each conversation.
        """
        y_true = []
        y_pred = []

        for convo in val_data["conversations"]:
            # True labels
            true_labels = SmellParser.extract_true_labels(convo)
            y_true.append(true_labels)

            # User message
            user_message = [msg for msg in convo if msg["role"] == "user"]

            # Model inference
            generated_response = model_inference.infer(user_message)
            if generated_response:
                pred_labels = SmellParser.parse_smells(
                    generated_response[0], self.valid_labels
                )
                y_pred.append(pred_labels)
            else:
                y_pred.append([])

        return y_true, y_pred

    def calculate_metrics(self, y_true, y_pred):
        """
        Calculates evaluation metrics for the model's performance.
        Args:
            y_true (list): Ground truth labels for each conversation.
            y_pred (list): Predicted labels for each conversation.

        Returns:
            tuple:
                - accuracy (float):
                    Accuracy of the model's predictions.
                - report (str):
                    A classification report detailing precision, recall,
                    and F1-score for each label.

        """
        all_labels = list(set(label for labels in y_true for label in labels))
        y_true_bin = np.array(
            [
                [1 if label in labels else 0 for label in all_labels]
                for labels in y_true
            ]  # E501
        )
        y_pred_bin = np.array(
            [
                [1 if label in labels else 0 for label in all_labels]
                for labels in y_pred
            ]  # E501
        )

        # Accuracy
        accuracy = np.mean(np.all(y_true_bin == y_pred_bin, axis=1))

        # Classification report
        report = classification_report(
            y_true_bin, y_pred_bin, target_names=all_labels, zero_division=0
        )

        return accuracy, report
