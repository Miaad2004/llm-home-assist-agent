from abc import ABC, abstractmethod
from typing import Dict, List, Union, Any, Optional


class LLMClientInterface(ABC):
    """
    Interface for interacting with an external large language model (LLM).
    """
    
    # History property to store conversation context
    history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def send_prompt(self, prompt: str, tools: Optional[List[Dict[str, Any]]] = None, tool_choice: Optional[str] = None) -> Any:
        """
        Sends a natural language prompt to the LLM.

        Args:
            prompt (str): The input prompt.
            tools (List[Dict[str, Any]], optional): List of tool definitions.
            tool_choice (str, optional): Control whether the model can use tools. 
                                         Options: "auto", "required", "none".

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