from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """
    Abstract base class for language models.
    """

    @abstractmethod
    def generate_response(self, prompt):
        """
        Generates a response from the language model for the given prompt.

        Args:
            prompt (str): The input text prompt.

        Returns:
            str: The generated response.
        """
        pass
