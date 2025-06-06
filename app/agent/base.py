from abc import ABC, abstractmethod
import pydantic
from typing import Dict, Any, Optional

class Response(pydantic.BaseModel):
    Question: str
    Thought: str
    tools_used: list[str]
    tool_arguments: Dict[str, Dict[str, Any]] = {}  
    Answer: Optional[str]

class ToolOutput(pydantic.BaseModel): 
    OriginalQuestion: str
    tools_used: list[str]
    tool_output: Dict[str, str]


class DeviceCommandAgent(ABC):
    """
    Abstract base class for handling user commands and device control.
    """

    @abstractmethod
    def handle_user_input(self, user_text: str) -> str:
        """
        Processes user input and returns a system response.
        """
        pass

    @abstractmethod
    def parse_llm_response(self, llm_output: str) -> Response:
        """
        Parses LLM output into a structured command.
        """
        pass

    @abstractmethod
    def call_tool(self, original_question: str, tools_used: list[str]) -> ToolOutput:
        """
        Executes a command using the device control layer.
        """
        pass