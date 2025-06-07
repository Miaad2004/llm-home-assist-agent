# Voice Endpoints Documentation

This document describes the Text-to-Speech (TTS) and Speech-to-Text (STT) endpoints added to the Smart Home Assistant API.

## Overview

The voice endpoints provide:

- Text-to-Speech synthesis capabilities
- Speech-to-Text transcription for audio files
- Live speech-to-text transcription
- Complete voice chat workflow (STT → Agent → TTS)

## Endpoints

### 1. Text-to-Speech Synthesis

#### `POST /tts/synthesize`

Converts text to speech and returns metadata about the generated audio.

**Request Body:**

```json
{
  "text": "Text to synthesize",
  "voice": "default" // Optional: voice selection
}
```

**Response:**

```json
{
  "message": "TTS synthesis completed for: 'Text to synthesize'",
  "voice": "default",
  "audio_file_path": "/tmp/audio_file.wav",
  "status": "success",
  "note": "TTS implementation is pending - this is a mock response with placeholder file"
}
```

#### `POST /tts/synthesize/file`

Converts text to speech and returns the audio file for download.

**Request Body:**

```json
{
  "text": "Text to synthesize",
  "voice": "default"
}
```

**Response:** Audio file (WAV format) for download

### 2. Speech-to-Text Transcription

#### `POST /stt/transcribe`

Transcribes an uploaded audio file to text.

**Request:** Multipart form data with audio file

- `audio_file`: Audio file (WAV, MP3, etc.)

**Response:**

```json
{
  "transcription": "Transcribed text from the audio file",
  "status": "success"
}
```

#### `POST /stt/live`

Starts live speech-to-text transcription from microphone.

**Request:** No body required

**Response:**

```json
{
  "transcription": "Live transcription result",
  "status": "success"
}
```

### 3. Voice Chat

#### `POST /voice/chat`

Complete voice interaction workflow: converts audio to text, processes with agent, and returns response.

**Request:** Multipart form data with audio file

- `audio_file`: Audio file containing voice message

**Response:**

```json
{
  "user_message": "Transcribed user message",
  "agent_response": "Agent's response to the message",
  "status": "success",
  "note": "Audio response generation pending TTS implementation"
}
```

## Implementation Status

### Current State (Mock Implementation)

- **TTS**: Returns placeholder audio files and metadata
- **STT**: Returns mock transcriptions based on file size and content
- **Voice Chat**: Fully functional with mock TTS/STT components

### Future Implementation

- **TTS**: Integration with Coqui TTS or Piper for actual audio synthesis
- **STT**: Integration with OpenAI Whisper for real audio transcription
- **Live STT**: Real-time microphone input processing
- **Voice Enhancement**: Noise reduction, voice activity detection

## Usage Examples

### Python Example

```python
import requests

# TTS Example
tts_response = requests.post("http://localhost:8000/tts/synthesize", json={
    "text": "Hello, smart home!",
    "voice": "default"
})

# STT Example
with open("audio.wav", "rb") as audio_file:
    files = {"audio_file": ("audio.wav", audio_file, "audio/wav")}
    stt_response = requests.post("http://localhost:8000/stt/transcribe", files=files)

# Voice Chat Example
with open("voice_message.wav", "rb") as audio_file:
    files = {"audio_file": ("voice_message.wav", audio_file, "audio/wav")}
    chat_response = requests.post("http://localhost:8000/voice/chat", files=files)
```

### JavaScript Example

```javascript
// TTS Example
const ttsResponse = await fetch("http://localhost:8000/tts/synthesize", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "Hello, smart home!", voice: "default" }),
});

// STT Example
const formData = new FormData();
formData.append("audio_file", audioFile);
const sttResponse = await fetch("http://localhost:8000/stt/transcribe", {
  method: "POST",
  body: formData,
});
```

## Testing

### Test Script

Run the provided test script to verify all endpoints:

```bash
python examples/test_voice_endpoints.py
```

### Web Interface

Open the provided HTML interface in a browser:

```bash
# Start the API server first
python app/api/main.py

# Then open in browser
examples/voice_interface.html
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (e.g., invalid file type)
- `500`: Server error (e.g., service not initialized)

Error responses include descriptive messages:

```json
{
  "detail": "Error description"
}
```

## Configuration

Voice services are automatically initialized when the API starts. The initialization includes:

- TTS service (`TTSImpl`)
- STT service (`WhisperSTT`)
- Integration with the main agent system

## Dependencies

The voice endpoints require:

- FastAPI
- Pydantic
- Python tempfile module
- Future: Whisper, Coqui TTS, or similar libraries

## Notes

- Current implementation provides mock functionality for development and testing
- File uploads are temporarily stored and automatically cleaned up
- All voice processing is currently done server-side
- Future versions will support real-time streaming and WebRTC integration
