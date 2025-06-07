from .base import VoiceAssistantInterface
import tempfile
import os
import re
from gradio_client import Client, handle_file
import shutil
import uuid
from config.settings import Settings
class TTSImpl:
    """
    Handles text-to-speech synthesis using Dia model.
    """
    def __init__(self):
        """Initialize Dia TTS client"""
        self.hf_token = Settings.HF_TOKEN
        self.client = None
        self.audio_prompt = 'https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav'
    def speak(self, message: str) -> None:
        """
        Input: str — Text message
        Output: None
        Calls: TTS engine (Coqui, Piper, etc.)
        """
        # TODO: Implement actual TTS synthesis
        print(f"[TTS] Speaking: {message}")
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
            print(f"[TTS] Formatted text: {formatted_text}")
                
            # Generate speech with Dia
            full_path = self._generate_with_dia(formatted_text, output_path)
            
            print(f"[TTS] Synthesized to file: {output_path}")
            
            # Return only the filename for security when using download folder
            return filename
                
        except Exception as e:
            print(f"[TTS Error] Synthesis failed: {e}")
            # Create placeholder file as fallback
            with open(output_path, 'w') as f:
                f.write(f"# Audio file placeholder for: {text}")
            return os.path.basename(output_path)
    
    def _generate_with_dia(self, formatted_text: str, output_path: str) -> str:
        """Generate speech using Dia model"""
        try:
            self._initialize_client()
            
            print("🎙️ Generating speech with Dia...")
            
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
            print(f"✅ Audio generated successfully: {output_path}")
            
            print(f"[TTS] Synthesized to file: {output_path}")
            
            return output_path
        except Exception as e:
            print(f"❌ TTS Generation failed: {str(e)}")
            raise  # Re-raise the exception to be caught by the caller

    def speak(self, message: str, voice: str = "female") -> None:
        """
        Synthesize and play text using Dia TTS.
        
        Args:
            message: Text message to speak
            voice: "male", "female", or "auto"
        """
        try:
            # Generate audio file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_path = temp_file.name
            temp_file.close()
            
            audio_path = self.synthesize_to_file(message, temp_path, voice)
            
            # Play the audio
            self._play_audio(audio_path)
            
            # Clean up temp file
            try:
                os.unlink(audio_path)
            except:
                pass
                
        except Exception as e:
            print(f"[TTS Error] Could not synthesize speech: {e}")
            # Fallback to text output
            print(f"[TTS Fallback] Speaking: {message}")
    

    def _play_audio(self, file_path: str):
        """Play audio file using system default player"""
        try:
            import sys
            import subprocess
            
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])
            print("🔊 Playing audio...")
        except Exception as e:
            print(f"❌ Could not play audio: {e}")

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
            print("🔄 Connecting to Dia-1.6B model...")
            self.client = Client("nari-labs/Dia-1.6B", hf_token=self.hf_token)