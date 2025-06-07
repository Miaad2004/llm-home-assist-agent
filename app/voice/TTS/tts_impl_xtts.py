from .base import VoiceAssistantInterface
import os
import torch
from TTS.api import TTS
from config.settings import Settings
from .base import VoiceAssistantInterface
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)

class XTTS_TTS(VoiceAssistantInterface):
    """
    Handles text-to-speech synthesis using XTTS model.
    """
    def __init__(self):
        """Initialize XTTS TTS engine"""
        # Get device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"{Fore.CYAN}Using device: {self.device}{Style.RESET_ALL}")
        
        # Model paths
        self.model_path = Settings.XTTS_PATH
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"XTTS model path does not exist: {self.model_path}")
        
        self.config_path = os.path.join(self.model_path, "config.json")
        
        # Lazy initialization
        self.tts = None
        self.speaker_male = Settings.XTTS_MALE_VOICE
        self.speaker_female = Settings.XTTS_FEMALE_VOICE
        self.speech_rate = Settings.XTTS_SPEED
        
        self._initialize_tts()

    def _initialize_tts(self):
        """Lazy initialization of the TTS model"""
        if self.tts is None:
            print(f"{Fore.YELLOW}Initializing XTTS model...{Style.RESET_ALL}")
            self.tts = TTS(model_path=self.model_path, config_path=self.config_path).to(self.device)

    
    def synthesize_to_file(self, text: str, output_path: str = None, voice: str = "male") -> str:
        """
        Synthesize text to an audio file.
        
        Args:
            text: Text to synthesize
            output_path: Optional path for output file. If None, creates file in download folder.
            voice: Speaker name or "male"/"female" for default voices
            speed: Speech rate multiplier (1.0 = normal, >1.0 = faster, <1.0 = slower)
            
        Returns:
            Filename (not full path) of the generated audio file in the download folder
        """
        try:
            
            self._initialize_tts()
            
            if output_path is None:
                # Create filename based on text hash for uniqueness
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                filename = f"tts_output_{text_hash}.wav"
                
                # Ensure download folder exists
                download_folder = Settings.DOWNLOAD_FOLDER_PATH
                os.makedirs(download_folder, exist_ok=True)
                
                # Create full path in download folder
                output_path = os.path.join(download_folder, filename)
                
            else:
                filename = os.path.basename(output_path)
            
            # Default to "Gracie Wise" if specified voice is "female"
            speaker = self.speaker_male if voice.lower() == "male" else self.speaker_female
            
            print(f"{Fore.YELLOW}Generating speech with XTTS...{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[TTS] Text: {text}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[TTS] Speaker: {speaker}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[TTS] Speed: {self.speech_rate}x{Style.RESET_ALL}")
            
            # Generate speech with XTTS
            self.tts.tts_to_file(
                text=text,
                speaker=speaker,
                language="en",
                file_path=output_path,
                #speed=self.speech_rate
            )
            
            print(f"{Fore.GREEN}Audio generated successfully: {output_path}{Style.RESET_ALL}")
            
            # Return only the filename for security when using download folder
            return filename
                
        except Exception as e:
            print(f"{Fore.RED}[TTS Error] Synthesis failed: {e}{Style.RESET_ALL}")
            raise e
