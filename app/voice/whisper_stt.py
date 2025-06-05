from .base import VoiceAssistantInterface


class WhisperSTT:
    """
    Handles speech-to-text transcription using Whisper.
    """

    def transcribe(self, audio_path: str) -> str:
        """
        Input: str — Path to audio file
        Output: str — Transcribed text
        Action: Transcribe audio to text using Whisper
        """
        # TODO: Implement Whisper transcription
        return "[STT] Transcribed text."
