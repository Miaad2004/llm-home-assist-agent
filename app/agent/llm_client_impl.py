from .base import LLMClientInterface

class GroqLLMClient(LLMClientInterface):
    """
    LLM client implementation for Groq API.
    """
    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Prompt
        Output: str — LLM response
        Action: Send prompt to Groq API and return response
        """
        # TODO: Implement Groq API call
        return "[Groq] LLM response."

class TogetherAILLMClient(LLMClientInterface):
    """
    LLM client implementation for TogetherAI API.
    """
    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Prompt
        Output: str — LLM response
        Action: Send prompt to TogetherAI API and return response
        """
        # TODO: Implement TogetherAI API call
        return "[TogetherAI] LLM response."
