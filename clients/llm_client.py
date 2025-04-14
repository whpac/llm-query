from abc import ABC, abstractmethod
from .model_response import ModelResponse

class LLMClient(ABC):

    @abstractmethod
    def ask(self, prompt: str) -> ModelResponse:
        """
        Send a prompt to the LLM and return the response.
        """
        pass
