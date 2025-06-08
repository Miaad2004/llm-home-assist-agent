from .base import VoiceAssistantInterface
import os
import whisper
#import sounddevice as sd
import numpy as np
import tempfile
#import scipy.io.wavfile
from config.settings import Settings
from colorama import Fore, Style, init
import shutil
import traceback

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Assigned to: Person B (Voice pipeline)
class WhisperSTT:
    """
    Handles speech-to-text transcription using Whisper.
    """
    
    def __init__(self, model_size="base"):
        """Initialize with specified Whisper model size"""
        self.model = None
        self.model_size = model_size
        self._load_model()  # Load model on initialization
    
    def _clear_corrupted_model(self, model_dir):
        """Clear corrupted model files from the directory"""
        # try:
        #     if os.path.exists(model_dir):
        #         print(f"{Fore.YELLOW}[STT] Clearing corrupted model files from {model_dir}{Style.RESET_ALL}")
        #         shutil.rmtree(model_dir)
        #         os.makedirs(model_dir, exist_ok=True)
                
        # except Exception as e:
        #     print(f"{Fore.RED}[STT] Warning: Could not clear model directory: {str(e)}{Style.RESET_ALL}")
        pass
    
    def _load_model(self):
        """Load the Whisper model if not already loaded"""
        if self.model is None:
            print(f"{Fore.CYAN}[STT] Loading Whisper {self.model_size} model...{Style.RESET_ALL}")
            
            # Use the local model file if it's the base model
            if self.model_size == "base":
                try:
                    local_model_path = Settings.WHISPER_MODEL_PATH
                    local_model_dir = os.path.dirname(local_model_path)
                    print(f"{Fore.CYAN}[STT DEBUG] Local model path: {local_model_path}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}[STT DEBUG] Local model directory: {local_model_dir}{Style.RESET_ALL}")
                    
                    # Try loading existing model first
                    if os.path.exists(local_model_path):
                        try:
                            print(f"{Fore.GREEN}[STT] Using local model file: {local_model_path}{Style.RESET_ALL}")
                            file_size = os.path.getsize(local_model_path)
                            print(f"{Fore.CYAN}[STT DEBUG] Model file size: {file_size} bytes{Style.RESET_ALL}")
                            self.model = whisper.load_model(local_model_path)
                            print(f"{Fore.GREEN}[STT] Model loaded successfully{Style.RESET_ALL}")
                            return self.model
                        except Exception as e:
                            print(f"{Fore.YELLOW}[STT] Local model file corrupted: {str(e)}{Style.RESET_ALL}")
                            print(f"{Fore.RED}[STT DEBUG] Corruption error details:{Style.RESET_ALL}")
                            print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                            self._clear_corrupted_model(local_model_dir)
                    else:
                        print(f"{Fore.YELLOW}[STT DEBUG] Local model file does not exist at: {local_model_path}{Style.RESET_ALL}")
                    
                    # Download model with retry logic
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            print(f"{Fore.YELLOW}[STT] Downloading model (attempt {attempt + 1}/{max_retries})...{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}[STT DEBUG] Creating directory: {local_model_dir}{Style.RESET_ALL}")
                            os.makedirs(local_model_dir, exist_ok=True)
                            print(f"{Fore.CYAN}[STT DEBUG] Starting Whisper model download...{Style.RESET_ALL}")
                            self.model = whisper.load_model(self.model_size, download_root=local_model_dir)
                            print(f"{Fore.GREEN}[STT] Model downloaded and loaded successfully{Style.RESET_ALL}")
                            break
                        except Exception as e:
                            print(f"{Fore.RED}[STT] Download attempt {attempt + 1} failed: {str(e)}{Style.RESET_ALL}")
                            print(f"{Fore.RED}[STT DEBUG] Download error details:{Style.RESET_ALL}")
                            print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                            if "checksum" in str(e).lower() or "sha256" in str(e).lower():
                                print(f"{Fore.YELLOW}[STT DEBUG] Checksum error detected, clearing corrupted files{Style.RESET_ALL}")
                                self._clear_corrupted_model(local_model_dir)
                            if attempt == max_retries - 1:
                                print(f"{Fore.RED}[STT] All download attempts failed. Falling back to online model.{Style.RESET_ALL}")
                                try:
                                    print(f"{Fore.CYAN}[STT DEBUG] Attempting fallback to online model{Style.RESET_ALL}")
                                    self.model = whisper.load_model(self.model_size)
                                    print(f"{Fore.GREEN}[STT] Fallback model loaded successfully{Style.RESET_ALL}")
                                except Exception as fallback_e:
                                    print(f"{Fore.RED}[STT] Fallback model loading failed: {str(fallback_e)}{Style.RESET_ALL}")
                                    print(f"{Fore.RED}[STT DEBUG] Fallback error details:{Style.RESET_ALL}")
                                    print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                                    raise fallback_e
                except Exception as e:
                    print(f"{Fore.RED}[STT] Critical error in model loading: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}[STT DEBUG] Critical error details:{Style.RESET_ALL}")
                    print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                    raise e
            else:
                try:
                    print(f"{Fore.CYAN}[STT DEBUG] Loading non-base model: {self.model_size}{Style.RESET_ALL}")
                    self.model = whisper.load_model(self.model_size)
                    print(f"{Fore.GREEN}[STT] Non-base model loaded successfully{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[STT] Non-base model loading failed: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}[STT DEBUG] Non-base model error details:{Style.RESET_ALL}")
                    print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                    raise e
                
            print(f"{Fore.GREEN}[STT] Model loaded successfully{Style.RESET_ALL}")
        return self.model

    def transcribe(self, audio_path: str) -> str:
        """
        Input: str — Path to audio file
        Output: str — Transcribed text
        Calls: Whisper STT engine
        """
        try:
            print(f"{Fore.CYAN}[STT DEBUG] Checking audio file: {audio_path}{Style.RESET_ALL}")
            if not os.path.exists(audio_path):
                print(f"{Fore.RED}[STT DEBUG] Audio file not found at path: {audio_path}{Style.RESET_ALL}")
                return "[STT Error] Audio file not found"
            
            # Check file size and permissions
            try:
                file_size = os.path.getsize(audio_path)
                print(f"{Fore.CYAN}[STT DEBUG] Audio file size: {file_size} bytes{Style.RESET_ALL}")
                if file_size == 0:
                    print(f"{Fore.RED}[STT DEBUG] Audio file is empty{Style.RESET_ALL}")
                    return "[STT Error] Audio file is empty"
            except Exception as e:
                print(f"{Fore.RED}[STT DEBUG] Error checking file size: {str(e)}{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}[STT DEBUG] Loading model for transcription{Style.RESET_ALL}")
            model = self._load_model()
            print(f"{Fore.CYAN}[STT] Transcribing file: {audio_path}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[STT DEBUG] Starting Whisper transcription...{Style.RESET_ALL}")
            result = model.transcribe(audio_path)
            print(f"{Fore.MAGENTA}{result['text']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[STT] Transcription complete{Style.RESET_ALL}")
            return result["text"]
        except Exception as e:
            print(f"{Fore.RED}[STT] Transcription error: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.RED}[STT DEBUG] Transcription error details:{Style.RESET_ALL}")
            print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
            return f"[STT Error] {str(e)}"

    def transcribe_live(self, silence_threshold=100, silence_duration=2, samplerate=16000) -> str:
        """
        Transcribe live audio from microphone.
        
        Returns:
            Transcribed text from live audio
        """
        try:
            print(f"{Fore.CYAN}[STT] Starting live transcription...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[STT DEBUG] Parameters - Threshold: {silence_threshold}, Duration: {silence_duration}s, Sample rate: {samplerate}Hz{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[STT] Recording... Speak now.{Style.RESET_ALL}")
            
            # Set up recording parameters
            chunk_duration = 2  # seconds
            chunk_samples = int(samplerate * chunk_duration)
            audio_chunks = []
            silence_chunks = 0
            max_silence_chunks = int(silence_duration / chunk_duration)
            print(f"{Fore.CYAN}[STT DEBUG] Chunk duration: {chunk_duration}s, Chunk samples: {chunk_samples}, Max silence chunks: {max_silence_chunks}{Style.RESET_ALL}")

            # Record audio with silence detection
            chunk_count = 0
            while True:
                try:
                    chunk = sd.rec(chunk_samples, samplerate=samplerate, channels=1, dtype='int16')
                    sd.wait()
                    audio_chunks.append(chunk)
                    chunk_count += 1
                    
                    # Check if audio is silent
                    rms = np.sqrt(np.mean(chunk.astype(np.float32)**2))
                    print(f"{Fore.CYAN}[STT DEBUG] Chunk {chunk_count}: RMS={rms:.2f}, Threshold={silence_threshold}{Style.RESET_ALL}")
                    
                    if rms < silence_threshold:
                        silence_chunks += 1
                        print(f"{Fore.YELLOW}[STT DEBUG] Silent chunk detected ({silence_chunks}/{max_silence_chunks}){Style.RESET_ALL}")
                    else:
                        silence_chunks = 0
                        print(f"{Fore.GREEN}[STT DEBUG] Audio detected, resetting silence counter{Style.RESET_ALL}")
                        
                    # Stop recording after sustained silence
                    if silence_chunks >= max_silence_chunks:
                        print(f"{Fore.CYAN}[STT DEBUG] Sustained silence detected, stopping recording{Style.RESET_ALL}")
                        break
                        
                except Exception as e:
                    print(f"{Fore.RED}[STT DEBUG] Error during recording chunk {chunk_count}: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                    break

            print(f"{Fore.CYAN}[STT DEBUG] Recorded {len(audio_chunks)} chunks, combining audio...{Style.RESET_ALL}")
            # Combine all audio chunks
            audio = np.concatenate(audio_chunks, axis=0)
            print(f"{Fore.CYAN}[STT DEBUG] Combined audio shape: {audio.shape}{Style.RESET_ALL}")

            # Save to temporary file for transcription
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_file = f.name
                print(f"{Fore.CYAN}[STT DEBUG] Saving audio to temporary file: {temp_file}{Style.RESET_ALL}")
                try:
                    scipy.io.wavfile.write(temp_file, samplerate, audio)
                    temp_file_size = os.path.getsize(temp_file)
                    print(f"{Fore.CYAN}[STT DEBUG] Temporary file size: {temp_file_size} bytes{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[STT DEBUG] Error writing temporary file: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                    raise e
                
                # Transcribe the audio
                print(f"{Fore.CYAN}[STT] Recording complete, transcribing...{Style.RESET_ALL}")
                try:
                    model = self._load_model()
                    print(f"{Fore.CYAN}[STT DEBUG] Starting transcription of temporary file{Style.RESET_ALL}")
                    result = model.transcribe(temp_file)
                    print(f"{Fore.GREEN}[STT DEBUG] Transcription result obtained{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[STT DEBUG] Error during transcription: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
                    raise e
                
                # Clean up
                try:
                    print(f"{Fore.CYAN}[STT DEBUG] Cleaning up temporary file{Style.RESET_ALL}")
                    os.unlink(temp_file)
                except Exception as e:
                    print(f"{Fore.YELLOW}[STT DEBUG] Warning: Could not delete temporary file: {str(e)}{Style.RESET_ALL}")
                    
                return result["text"]
                
        except Exception as e:
            print(f"{Fore.RED}[STT] Live transcription error: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.RED}[STT DEBUG] Live transcription error details:{Style.RESET_ALL}")
            print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
            return f"[STT Error] Live transcription failed: {str(e)}"
