from abc import ABC, abstractmethod

class VoiceAssistantInterface(ABC):
    """
    Handles wake word detection, speech recognition, and text-to-speech responses.

    Role:
    - Listen for "Hey Assistant"
    - Transcribe audio to text using Whisper
    - Synthesize LLM responses for audible output
    """

    @abstractmethod
    def wait_for_command(self) -> str:
        """
        Input: None
        Output: str — Transcribed user voice command (e.g., "Turn off the kitchen lamp")
        Called by: SmartHomeUIManager
        Calls: wake word engine, STT model
        """
        pass

    @abstractmethod
    def speak(self, message: str) -> None:
        """
        Input: str — Text message to synthesize as audio
        Output: None
        Called by: SmartHomeUIManager, DeviceCommandAgent (optionally)
        Calls: TTS model
        """
        pass
