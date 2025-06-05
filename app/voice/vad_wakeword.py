from .base import VoiceAssistantInterface

# Assigned to: Person B (Voice pipeline)
class VADWakeword:
    """
    Handles wake word detection and voice activity detection.
    """

    def detect(self, audio_path: str) -> bool:
        """
        Input: str — Path to audio file
        Output: bool — True if wake word detected
        Calls: Wakeword/VAD engine
        """
        # TODO: Implement wake word detection
        return False
