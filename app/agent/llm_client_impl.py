from .base import LLMClientInterface

# Assigned to: Person A (UI LLM integration)
class GroqLLMClient(LLMClientInterface):
    """
    LLM client implementation for Groq API.
    """
    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Prompt
        Output: str — LLM response
        Calls: Groq API
        """
        # TODO: Implement Groq API call
        return "[Groq] LLM response."

# Assigned to: Person B (Voice LLM integration)
class TogetherAILLMClient(LLMClientInterface):
    """
    LLM client implementation for TogetherAI API.
    """
    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Prompt
        Output: str — LLM response
        Calls: TogetherAI API
        """
        # TODO: Implement TogetherAI API call
        return "[TogetherAI] LLM response."
