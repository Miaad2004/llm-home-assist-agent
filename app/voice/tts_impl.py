from .base import VoiceAssistantInterface

# Assigned to: Person B (Voice pipeline)
class TTSImpl:
    """
    Handles text-to-speech synthesis using Coqui or Piper.
    """

    def speak(self, message: str) -> None:
        """
        Input: str — Text message
        Output: None
        Calls: TTS engine (Coqui, Piper, etc.)
        """
        # TODO: Implement TTS synthesis
        pass
