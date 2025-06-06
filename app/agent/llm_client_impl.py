from .llm_client import LLMClientInterface
import openai

class GenericOpenAILLMClient(LLMClientInterface):
    """
    Generic LLM client implementation using the openai library.
    Can be configured for any LLM endpoint supported by openai.
    """
    def __init__(self, api_key: str, model: str, api_base: str = ""):  # default to empty string
        """
        api_key: str — API key for the LLM provider
        model: str — Model name (e.g., "gpt-3.5-turbo", "groq/model", "togetherai/model")
        api_base: str — Optional custom API endpoint
        """
        self.api_key = api_key
        self.model = model
        self.api_base = api_base or None

    def send_prompt(self, prompt: str) -> str:
        """
        Input: str — Prompt
        Output: str — LLM response
        Calls: openai.resources.chat.completions.create (openai>=1.0.0)
        """
        openai.api_key = self.api_key
        if self.api_base:
            openai.base_url = self.api_base  # openai>=1.0.0 uses base_url
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            # openai>=1.0.0: response.choices[0].message.content
            return response.choices[0].message.content
        except Exception as e:
            return f"[Error] {str(e)}"
