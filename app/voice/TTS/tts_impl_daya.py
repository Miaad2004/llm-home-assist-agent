from .base import VoiceAssistantInterface
import tempfile
import os
import re
from gradio_client import Client, handle_file
import shutil
from config.settings import Settings
from .base import VoiceAssistantInterface
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)


class DAYA_TTS(VoiceAssistantInterface):
    """
    Handles text-to-speech synthesis using Dia model.
    """
    def __init__(self):
        """Initialize Dia TTS client"""
        self.hf_token = Settings.HF_TOKEN
        self.client = None
        self.audio_prompt = 'https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav'
        

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
        try:
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
            
            # Format text for Dia model
            formatted_text = self._format_text_for_dia(text, voice)
            print(f"{Fore.BLUE}[TTS] Formatted text: {formatted_text}{Style.RESET_ALL}")
                
            # Generate speech with Dia
            full_path = self._generate_with_dia(formatted_text, output_path)
            
            print(f"{Fore.GREEN}[TTS] Synthesized to file: {output_path}{Style.RESET_ALL}")
            
            # Return only the filename for security when using download folder
            return filename
                
        except Exception as e:
            print(f"{Fore.RED}[TTS Error] Synthesis failed: {e}{Style.RESET_ALL}")
            # Create placeholder file as fallback
            with open(output_path, 'w') as f:
                f.write(f"# Audio file placeholder for: {text}")
            return os.path.basename(output_path)
    
    def _generate_with_dia(self, formatted_text: str, output_path: str) -> str:
        """Generate speech using Dia model"""
        try:
            self._initialize_client()
            
            print(f"{Fore.YELLOW}Generating speech with Dia...{Style.RESET_ALL}")
            
            result = self.client.predict(
                text_input=formatted_text,
                audio_prompt_input=handle_file(self.audio_prompt),
                max_new_tokens=3072,
                cfg_scale=3,
                temperature=1.3,
                top_p=0.95,
                cfg_filter_top_k=30,
                speed_factor=0.94,
                api_name="/generate_audio"
            )
            
            # Verify result is valid before proceeding
            if not result or not os.path.exists(result):
                raise ValueError(f"Dia TTS returned invalid result: {result}")
            
            # Copy the generated audio to the specified output path
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            shutil.copy2(result, output_path)
            print(f"{Fore.GREEN}Audio generated successfully: {output_path}{Style.RESET_ALL}")
            
            print(f"{Fore.GREEN}[TTS] Synthesized to file: {output_path}{Style.RESET_ALL}")
            
            return output_path
        except Exception as e:
            print(f"{Fore.RED}TTS Generation failed: {str(e)}{Style.RESET_ALL}")
            raise  # Re-raise the exception to be caught by the caller

    def _format_text_for_dia(self, text: str, voice: str = "female") -> str:
        """
        Format text for the Dia TTS model with appropriate speaker tags.
        
        Args:
            text: The text to be synthesized
            voice: "male", "female", or "auto" voice selection
                (Note: All formats must alternate [S1] and [S2] per Dia requirements)
                
        Returns:
            Formatted text string for Dia model
        """
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        formatted_parts = []
        
        # Dia requires alternating speakers regardless of voice type
        # Always start with [S1]
        for i, sentence in enumerate(sentences):
            # For single sentences, always use [S1]
            if len(sentences) == 1:
                formatted_parts.append(f"[S1] {sentence}.")
                break
                
            # For multiple sentences, alternate between [S1] and [S2]
            # We always start with [S1]
            speaker_tag = "[S1]" if i % 2 == 0 else "[S2]"
            
            # Add space after tag and ensure sentence ends with punctuation
            if not sentence.endswith(('.', '!', '?')):
                formatted_parts.append(f"{speaker_tag} {sentence}.")
            else:
                formatted_parts.append(f"{speaker_tag} {sentence}")
        
        # Join all formatted sentences with spaces
        return " ".join(formatted_parts)

    def _initialize_client(self):
        """Lazy initialization of the Dia client"""
        if self.client is None:
            print(f"{Fore.YELLOW}Connecting to Dia-1.6B model...{Style.RESET_ALL}")
            self.client = Client("nari-labs/Dia-1.6B", hf_token=self.hf_token)