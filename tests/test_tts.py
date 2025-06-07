import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Initialize TTS
tts = TTS(model_path="D:\\Uni\\Term_6\\DM\\Agent\\smart-home-assistant\\tts_model", config_path="D:\\Uni\\Term_6\\DM\\Agent\\smart-home-assistant\\tts_model\\config.json").to(device)

# List speakers
print(tts.speakers)

# Run TTS
# ❗ XTTS supports both, but many models allow only one of the `speaker` and
# `speaker_wav` arguments

# TTS to a file, use a preset speaker
tts.tts_to_file(
  text="ahhhhhhh I know Mohammad Hossein. Wow! amazing! try it on github",
  speaker="Gracie Wise",
  language="en",
  file_path="output2.wav"
)