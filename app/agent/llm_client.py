from abc import ABC, abstractmethod

class LLMClientInterface(ABC):
    """
    Encapsulates communication with an external large language model (LLM).

    Role:
    - Abstracts away the LLM provider (Groq, TogetherAI)
    - Allows mocking and modular replacement
    """

    # Assigned to: Person A (UI LLM integration)
    @abstractmethod
    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Natural language prompt
        Output: str — Response text from LLM
        Called by: DeviceCommandAgentImpl.handle_user_input(), Voice pipeline
        Calls: External LLM API
        """
        pass
