from abc import ABC, abstractmethod

class LLMClientInterface(ABC):
    """
    Encapsulates communication with an external large language model (LLM).

    Role:
    - Abstracts away the LLM provider (Groq, TogetherAI)
    - Allows mocking and modular replacement
    """

    @abstractmethod
    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Natural language prompt
        Output: str — Response text from LLM
        Called by: DeviceCommandAgent
        Calls: External LLM API
        """
        pass
