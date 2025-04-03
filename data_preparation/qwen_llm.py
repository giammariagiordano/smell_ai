import ollama
from data_preparation.base_llm import BaseLLM


class QwenLLM(BaseLLM):
    """
    A class to manage the Qwen2.5-Coder model using Ollama for text generation.
    """

    def __init__(self, model_name="qwen2.5-coder:14b"):
        """
        Initializes the Qwen LLM model for use with Ollama.

        Args:
            model_name (str): The name of the Qwen model to use with Ollama.
        """
        self.model_name = model_name

    def generate_response(self, prompt):
        """
        Generates a response from the Qwen model using
        Ollama for the given prompt.

        Args:
            prompt (str): The input text prompt.

        Returns:
            str: The generated response.
        """
        # Call Ollama to generate the response
        response = ollama.generate(model=self.model_name, prompt=prompt)

        # Return the text part of the response
        return response["response"]
