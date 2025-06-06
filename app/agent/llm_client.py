from abc import ABC, abstractmethod
from typing import Dict, List, Union, Any, Optional


class LLMClientInterface(ABC):
    """
    Interface for interacting with an external large language model (LLM).
    """

    @abstractmethod
    def send_prompt(self, prompt: str, tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        """
        Sends a natural language prompt to the LLM.

        Args:
            prompt (str): The input prompt.
            tools (List[Dict[str, Any]], optional): List of tool definitions.

        Returns:
            Any: The response from the LLM, either as a string or a message object.
        """
        pass
    
    @abstractmethod
    def update_system_prompt(self, system_prompt: str):
        """
        Updates the system prompt used by the LLM.

        Args:
            system_prompt (str): The new system prompt.
        """
        pass