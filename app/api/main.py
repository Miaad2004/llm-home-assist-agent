from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
import tempfile
import io
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.agent.llm_client_impl import GenericLLMClient
from app.agent.agent_impl import MyAgent
from app.tools.tools import TOOLS
from app.voice.tts_impl import TTSImpl
from app.voice.whisper_stt import WhisperSTT
from config.settings import Settings
from app.devices.hardware import ArduinoController

# Initialize FastAPI app
app = FastAPI(
    title="Smart Home Assistant API",
    description="REST API for interacting with the Smart Home Assistant LLM",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store the agent and LLM client
agent = None
llm_client = None
tts_service = None
stt_service = None
device_controller = None

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    use_tools: Optional[bool] = True

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

class SystemPromptRequest(BaseModel):
    system_prompt: str

class HealthResponse(BaseModel):
    status: str
    message: str

class LLMConfigRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None
    api_base: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"

class STTResponse(BaseModel):
    transcription: str
    status: str = "success"

# Device control models
class Device(BaseModel):
    id: str
    name: str
    description: str
    type: str  # ac, lamp, tv, etc.
    location: str
    pin: int
    status: str

class DeviceList(BaseModel):
    devices: List[Device]

class DeviceControlRequest(BaseModel):
    device_id: str
    action: str  # "on" or "off"

class DeviceResponse(BaseModel):
    message: str
    status: str = "success"

# Initialize the agent and LLM client
def initialize_agent():
    global agent, llm_client, tts_service, stt_service, device_controller
    try:
        # Initialize LLM client
        llm_client = GenericLLMClient()
          # Initialize device controller
        device_controller = ArduinoController()
        
        # Set the device controller for the tools
        from app.tools.generic_tools import device_controller as tools_device_controller
        tools_device_controller = device_controller
        
        # Get all available tools
        tools = TOOLS
        
        # Initialize agent with tools
        agent = MyAgent(
            llm_client=llm_client,
            tools=tools,
            base_sys_prompt_path=Settings.SYSTEM_PROMPT_PATH or "",
            device_control=device_controller
        )
        
        # Initialize voice services
        tts_service = TTSImpl()
        stt_service = WhisperSTT()
        
        print("✅ Agent, voice services, and device controller initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False

# Startup event
@app.on_event("startup")
async def startup_event():
    initialize_agent()

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is running and the agent is initialized."""
    if agent is None or llm_client is None:
        return HealthResponse(
            status="error",
            message="Agent not initialized"
        )
    return HealthResponse(
        status="healthy",
        message="API is running and agent is initialized"
    )

# Simple chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the LLM and get a response."""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Process user input through the agent
        response = agent.handle_user_input(request.message)
        
        return ChatResponse(
            response=response,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Direct LLM interaction endpoint (without tools)
@app.post("/llm/direct", response_model=ChatResponse)
async def direct_llm_chat(request: ChatRequest):
    """Send a message directly to the LLM without using tools."""
    if llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    
    try:
        # Send prompt directly to LLM
        response = llm_client.send_prompt(request.message)
        
        # Handle both string and message object responses
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        return ChatResponse(
            response=response_text,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing LLM request: {str(e)}")

# Update system prompt endpoint
@app.post("/llm/system-prompt")
async def update_system_prompt(request: SystemPromptRequest):
    """Update the system prompt for the LLM."""
    if llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    
    try:
        llm_client.update_system_prompt(request.system_prompt)
        return {"status": "success", "message": "System prompt updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating system prompt: {str(e)}")

# Get current system prompt
@app.get("/llm/system-prompt")
async def get_system_prompt():
    """Get the current system prompt."""
    if llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    
    try:
        return {
            "system_prompt": llm_client.system_prompt,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system prompt: {str(e)}")

# Clear conversation history
@app.post("/llm/clear-history")
async def clear_history():
    """Clear the conversation history."""
    if llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    
    try:
        # Reset history to just the system prompt
        llm_client.history = [{"role": "system", "content": llm_client.system_prompt}] if llm_client.system_prompt else []
        return {"status": "success", "message": "Conversation history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")

# Get conversation history
@app.get("/llm/history")
async def get_history():
    """Get the current conversation history."""
    if llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    
    try:
        return {
            "history": llm_client.history,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")

# Reinitialize agent endpoint
@app.post("/agent/reinitialize")
async def reinitialize_agent():
    """Reinitialize the agent and LLM client."""
    try:
        success = initialize_agent()
        if success:
            return {"status": "success", "message": "Agent reinitialized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reinitialize agent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reinitializing agent: {str(e)}")

# Get available tools
@app.get("/tools")
async def get_available_tools():
    """Get a list of available tools."""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        tools_info = []
        for tool_name, tool_info in agent.tools.items():
            # Get description from the tool info dictionary
            description = tool_info.get('description', 'No description available')
            if not description or description == 'No description available':
                # Fallback to function docstring
                description = tool_info.get('function_docstring', 'No description available')
            
            tool_data = {
                "name": tool_name,
                "description": description,
                "parameters": tool_info.get('parameters', {})            }
            tools_info.append(tool_data)
        
        return {
            "tools": tools_info,
            "count": len(tools_info),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")

# Text-to-Speech endpoint
@app.post("/tts/synthesize")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech and return audio file metadata."""
    if tts_service is None:
        raise HTTPException(status_code=500, detail="TTS service not initialized")
    
    try:
        # Generate audio file (returns filename only for security)
        audio_filename = tts_service.synthesize_to_file(request.text)
        
        # Return filename and metadata
        return {
            "message": f"TTS synthesis completed for: '{request.text}'",
            "voice": request.voice,
            "audio_filename": audio_filename,
            "download_url": f"/files/download?filename={audio_filename}",
            "status": "success",
            "note": "TTS implementation is pending - this is a mock response with placeholder file"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in TTS synthesis: {str(e)}")

# Text-to-Speech endpoint that returns audio file
@app.post("/tts/synthesize/file")
async def text_to_speech_file(request: TTSRequest):
    """Convert text to speech and return the audio file for download."""
    if tts_service is None:
        raise HTTPException(status_code=500, detail="TTS service not initialized")
    
    try:
        from config.settings import Settings
        
        # Generate audio file (returns filename only)
        audio_filename = tts_service.synthesize_to_file(request.text)
        
        # Construct full path from download folder and filename
        download_folder = Settings.DOWNLOAD_FOLDER_PATH
        audio_file_path = os.path.join(download_folder, audio_filename)
        
        # Return the file for download
        return FileResponse(
            path=audio_file_path,
            media_type='audio/wav',
            filename=audio_filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in TTS synthesis: {str(e)}")

# Secure file download endpoint
@app.get("/files/download")
async def download_file(filename: str):
    """Download a file by filename from the secure download folder.
    
    Args:
        filename: The name of the file to download (filename only, no paths)
        
    Returns:
        FileResponse with the requested file from the download folder
        
    Security: Only allows downloading files from the designated download folder.
    Prevents directory traversal attacks by validating filename and checking folder.
    """
    try:
        from config.settings import Settings
        
        # Security check: ensure filename contains no path separators
        if '/' in filename or '\\' in filename or '..' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename: path separators not allowed")
        
        # Construct the full file path within the download folder
        download_folder = Settings.DOWNLOAD_FOLDER_PATH
        file_path = os.path.join(download_folder, filename)
        
        # Normalize paths to prevent directory traversal
        download_folder = os.path.abspath(download_folder)
        file_path = os.path.abspath(file_path)
        
        # Security check: ensure the resolved path is within the download folder
        if not file_path.startswith(download_folder):
            raise HTTPException(status_code=403, detail="Access denied: file outside download folder")
        
        # Check if file exists and is a file
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Determine media type based on file extension
        file_extension = os.path.splitext(filename)[1].lower()
        media_type_map = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        media_type = media_type_map.get(file_extension, 'application/octet-stream')
        
        # Return the file for download
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

# Speech-to-Text endpoint
@app.post("/stt/transcribe", response_model=STTResponse)
async def speech_to_text(audio_file: UploadFile = File(...)):
    """Transcribe uploaded audio file to text."""
    if stt_service is None:
        raise HTTPException(status_code=500, detail="STT service not initialized")
    
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
          # Create temporary file for audio processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio using STT service
            transcription = stt_service.transcribe(temp_file_path)
            
            return STTResponse(
                transcription=transcription,
                status="success"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in STT transcription: {str(e)}")

# Live Speech-to-Text endpoint
@app.post("/stt/live", response_model=STTResponse)
async def live_speech_to_text():
    """Start live speech-to-text transcription from microphone."""
    if stt_service is None:
        raise HTTPException(status_code=500, detail="STT service not initialized")
    
    try:
        # Start live transcription
        transcription = stt_service.transcribe_live()
        
        return STTResponse(
            transcription=transcription,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in live STT: {str(e)}")

# Voice chat endpoint (combines STT + Chat + TTS)
@app.post("/voice/chat")
async def voice_chat(audio_file: UploadFile = File(...)):
    """Complete voice interaction: STT -> Chat -> TTS response."""
    if agent is None or stt_service is None or tts_service is None:
        raise HTTPException(status_code=500, detail="Voice services not fully initialized")
    
    try:
        # Step 1: Transcribe audio to text
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            user_message = stt_service.transcribe(temp_file_path)
            
            # Step 2: Process with agent
            agent_response = agent.handle_user_input(user_message)
            
            # Step 3: For now, return text response (TTS synthesis would happen here)
            return {
                "user_message": user_message,
                "agent_response": agent_response,
                "status": "success",
                "note": "Audio response generation pending TTS implementation"
            }
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in voice chat: {str(e)}")

# Device control endpoints
@app.get("/devices", response_model=DeviceList)
async def get_devices():
    """
    Get a list of all available devices and their current status.
    """
    global device_controller
    
    if not device_controller:
        raise HTTPException(status_code=503, detail="Device controller not initialized")
    
    try:
        device_dict = device_controller.get_device_states()
        # Convert dict to list of devices
        devices = list(device_dict.values()) if isinstance(device_dict, dict) else device_dict
        return DeviceList(devices=devices)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving devices: {str(e)}")

@app.post("/devices/control", response_model=DeviceResponse)
async def control_device(request: DeviceControlRequest):
    """
    Control a specific device by ID (turn it on or off).
    """
    global device_controller
    
    if not device_controller:
        raise HTTPException(status_code=503, detail="Device controller not initialized")
    
    # Validate action
    if request.action not in ["on", "off"]:
        raise HTTPException(status_code=400, detail="Action must be 'on' or 'off'")
    
    try:
        result = device_controller.control_device({
            "device_id": request.device_id,
            "action": request.action
        })
        
        # If the result starts with "Error", treat it as an error
        if result.startswith("Error"):
            raise HTTPException(status_code=400, detail=result)
            
        return DeviceResponse(message=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error controlling device: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)