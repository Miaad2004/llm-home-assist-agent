
from abc import ABC, abstractmethod

class VoiceAssistantInterface(ABC):
    """
    Interface for text-to-speech synthesis.
    """
    @abstractmethod
    def synthesize_to_file(self, text: str, output_path: str = None, voice: str = "female") -> str:
        """
        Synthesize text to an audio file.
        
        Args:
            text: Text to synthesize
            output_path: Optional path for output file. If None, creates file in download folder.
            voice: "male", "female", or "auto"
            
        Returns:
            Filename (not full path) of the generated audio file in the download folder
        """
        pass