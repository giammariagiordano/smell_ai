import json
import time
import requests
import logging
import re
# When running locally
from webapp.services.aiservice.app.schemas.responses import Smell
# When running with Docker
"""from app.schemas.responses import Smell"""


class Model:
    """
    Class to interact with the Ollama model for code smell detection.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:11434/api/generate",
        model_name: str = "codesmile:latest",
    ):
        """
        Initialize the Model instance.

        :param api_url: The URL of the Ollama API endpoint.
        :param model_name: The name of the Ollama model to be used.
        """
        self.api_url = api_url
        self.model_name = model_name
        self.logger = logging.getLogger("Model")
        logging.basicConfig(level=logging.INFO)

    def detect_code_smell(self, code_snippet: str) -> dict:
        """
        Perform AI-based code smell detection.

        :param code_snippet: The Python code snippet to analyze.
        :return: A dictionary containing the analysis results.
        """
        start_time = time.time()
        try:
            prompt = (
                f"You are an assistant trained to detect "
                "code smells in Python code.\n\n"
                f"Here is the code:\n{code_snippet}\n\n"
                f"Identify the code smell in the above code."
            )
            payload = {"model": self.model_name, "prompt": prompt}
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60,
                stream=True
            )

            if response.status_code != 200:
                self.logger.error(
                    "Ollama API responded with status code "
                    f"{response.status_code}: {response.text}"
                )
                return {"success": False,
                        "label": "Error in AI model analysis"}

            if not response.content:
                self.logger.error("Ollama API returned an empty response.")
                return {"success": False, "label": "No response from AI model"}

            # Initialize to reconstruct the response
            complete_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:  # Process each line of streamed response
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            complete_response += chunk["response"]
                    except json.JSONDecodeError as e:
                        self.logger.error(
                            f"Error decoding JSON chunk: {line} | {e}")

            # Log and validate the reassembled response
            if not complete_response:
                self.logger.warning(
                    "No valid response content reassembled from stream.")
                return {"success": False,
                        "label": "Incomplete response from AI model"}

            # Parse the final response for the code smell
            smells = self.parse_smell(complete_response)
            return {"success": True, "smells": smells}

        except requests.exceptions.Timeout:
            self.logger.error("Request timed out.")

        except ValueError:
            self.logger.error(f"Invalid JSON response: {response.text}")
            return {"success": False,
                    "label": "Invalid JSON response from AI model"}

        except requests.RequestException as e:
            self.logger.error(
                f"Error while communicating with the Ollama API: {e}")
            return {"success": False,
                    "label": "Error in communication with the AI model"}

        finally:
            elapsed_time = time.time() - start_time
            self.logger.info(f"Request completed in {elapsed_time} seconds.")

    @staticmethod
    def parse_smell(response_text: str) -> list[Smell]:
        """
        Parse the response from the model to extract the detected smells.

        Args:
            response_text (str): Raw response from the model.

        Returns:
            list[Smell]: List of detected smells as Smell objects.
        """
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

        # Extract the "The code smells are:" section
        match = re.search(
            r"The code smells are:(.*?)$",
            response_text,
            re.DOTALL
        )
        if not match:
            logging.warning(
                "No 'The code smells are:' section found in response.")
            return []

        # Extract all lines starting with "- "
        raw_labels = re.findall(r"- (.+)", match.group(1))

        smells = []
        for label in raw_labels:
            # Clean the label and validate against known smells
            label = label.split(":")[0].strip()
            if label in valid_labels:
                smells.append(Smell(smell_name=label))
            else:
                logging.warning(f"Unrecognized label: {label}")

        return smells
