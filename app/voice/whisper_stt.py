from .base import VoiceAssistantInterface

# Assigned to: Person B (Voice pipeline)
class WhisperSTT:
    """
    Handles speech-to-text transcription using Whisper.
    """

    def transcribe(self, audio_path: str) -> str:
        """
        Input: str — Path to audio file
        Output: str — Transcribed text
        Calls: Whisper STT engine
        """
        # TODO: Implement Whisper transcription
        return "[STT] Transcribed text."
