from .base import VoiceAssistantInterface
import os
import whisper
#import sounddevice as sd
import numpy as np
import tempfile
#import scipy.io.wavfile
from config.settings import Settings

# Assigned to: Person B (Voice pipeline)
class WhisperSTT:
    """
    Handles speech-to-text transcription using Whisper.
    """
    
    def __init__(self, model_size="base"):
        """Initialize with specified Whisper model size"""
        self.model = None
        self.model_size = model_size
    
    def _load_model(self):
        """Load the Whisper model if not already loaded"""
        if self.model is None:
            print(f"[STT] Loading Whisper {self.model_size} model...")
            
            # Use the local model file if it's the base model
            if self.model_size == "base":
                local_model_path = Settings.WHISPER_MODEL_PATH
                if os.path.exists(local_model_path):
                    print(f"[STT] Using local model file: {local_model_path}")
                    self.model = whisper.load_model(local_model_path)
                else:
                    print(f"[STT] Local model file not found, downloading model...")
                    self.model = whisper.load_model(self.model_size)
            else:
                self.model = whisper.load_model(self.model_size)
                
            print("[STT] Model loaded successfully")
        return self.model

    def transcribe(self, audio_path: str) -> str:
        """
        Input: str — Path to audio file
        Output: str — Transcribed text
        Calls: Whisper STT engine
        """
        try:
            if not os.path.exists(audio_path):
                return "[STT Error] Audio file not found"
            
            model = self._load_model()
            print(f"[STT] Transcribing file: {audio_path}")
            result = model.transcribe(audio_path)
            print(result["text"])
            print("[STT] Transcription complete")
            return result["text"]
        except Exception as e:
            return f"[STT Error] {str(e)}"

    def transcribe_live(self, silence_threshold=100, silence_duration=2, samplerate=16000) -> str:
        """
        Transcribe live audio from microphone.
        
        Returns:
            Transcribed text from live audio
        """
        try:
            print("[STT] Starting live transcription...")
            print("[STT] Recording... Speak now.")
            
            # Set up recording parameters
            chunk_duration = 2  # seconds
            chunk_samples = int(samplerate * chunk_duration)
            audio_chunks = []
            silence_chunks = 0
            max_silence_chunks = int(silence_duration / chunk_duration)

            # Record audio with silence detection
            while True:
                chunk = sd.rec(chunk_samples, samplerate=samplerate, channels=1, dtype='int16')
                sd.wait()
                audio_chunks.append(chunk)
                
                # Check if audio is silent
                rms = np.sqrt(np.mean(chunk.astype(np.float32)**2))
                if rms < silence_threshold:
                    silence_chunks += 1
                else:
                    silence_chunks = 0
                    
                # Stop recording after sustained silence
                if silence_chunks >= max_silence_chunks:
                    break

            # Combine all audio chunks
            audio = np.concatenate(audio_chunks, axis=0)

            # Save to temporary file for transcription
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_file = f.name
                scipy.io.wavfile.write(temp_file, samplerate, audio)
                
                # Transcribe the audio
                print("[STT] Recording complete, transcribing...")
                model = self._load_model()
                result = model.transcribe(temp_file)
                
                # Clean up
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
                return result["text"]
                
        except Exception as e:
            return f"[STT Error] Live transcription failed: {str(e)}"
