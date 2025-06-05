from .base import VoiceAssistantInterface


class TTSImpl:
    """
    Handles text-to-speech synthesis using Coqui or Piper.
    """

    def speak(self, message: str) -> None:
        """
        Input: str — Text message
        Output: None
        Action: Synthesize speech from text
        """
        # TODO: Implement TTS synthesis
        pass
