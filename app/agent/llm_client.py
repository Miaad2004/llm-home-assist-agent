from abc import ABC, abstractmethod
from typing import Dict, List, Union, Any


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
        
    @abstractmethod
    def send_prompt_with_functions(self, messages: List[Dict[str, str]], functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Input: 
            messages: List[Dict[str, str]] — Conversation messages
            functions: List[Dict[str, Any]] — Function definitions
        Output: Dict[str, Any] — Response from LLM with possible function calls
        Called by: DeviceCommandAgentImpl.handle_user_input()
        Calls: External LLM API
        """
        pass
