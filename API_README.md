# Smart Home Assistant REST API

This document describes the REST API for the Smart Home Assistant, which provides simple endpoints for interacting with the LLM and managing the assistant's functionality.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

**Windows (PowerShell):**

```powershell
.\start_api.ps1
```

**Python (Cross-platform):**

```bash
python scripts/start_api.py
```

### 3. Access the API

- **Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## API Endpoints

### Health Check

- **GET** `/health`
- **Description**: Check if the API is running and the agent is initialized
- **Response**:
  ```json
  {
    "status": "healthy",
    "message": "API is running and agent is initialized"
  }
  ```

### Chat Endpoints

#### Smart Chat (with Tools)

- **POST** `/chat`
- **Description**: Send a message to the assistant with access to tools
- **Request Body**:
  ```json
  {
    "message": "What's the weather like in New York?",
    "use_tools": true
  }
  ```
- **Response**:
  ```json
  {
    "response": "The current weather in New York is...",
    "status": "success"
  }
  ```

#### Direct LLM Chat

- **POST** `/llm/direct`
- **Description**: Send a message directly to the LLM without using tools
- **Request Body**:
  ```json
  {
    "message": "Tell me a joke"
  }
  ```
- **Response**:
  ```json
  {
    "response": "Why don't scientists trust atoms? Because they make up everything!",
    "status": "success"
  }
  ```

### System Prompt Management

#### Update System Prompt

- **POST** `/llm/system-prompt`
- **Description**: Update the system prompt for the LLM
- **Request Body**:
  ```json
  {
    "system_prompt": "You are a helpful assistant that always responds with enthusiasm!"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "System prompt updated"
  }
  ```

#### Get System Prompt

- **GET** `/llm/system-prompt`
- **Description**: Get the current system prompt
- **Response**:
  ```json
  {
    "system_prompt": "You are a helpful assistant...",
    "status": "success"
  }
  ```

### Conversation Management

#### Clear History

- **POST** `/llm/clear-history`
- **Description**: Clear the conversation history
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Conversation history cleared"
  }
  ```

#### Get History

- **GET** `/llm/history`
- **Description**: Get the current conversation history
- **Response**:
  ```json
  {
    "history": [
      { "role": "system", "content": "You are a helpful assistant..." },
      { "role": "user", "content": "Hello!" },
      { "role": "assistant", "content": "Hi there! How can I help you today?" }
    ],
    "status": "success"
  }
  ```

### Tools and Agent Management

#### Get Available Tools

- **GET** `/tools`
- **Description**: Get a list of available tools
- **Response**:
  ```json
  {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get the current weather for a specified city."
      },
      {
        "name": "get_news",
        "description": "Get the latest news articles..."
      }
    ],
    "count": 2,
    "status": "success"
  }
  ```

#### Reinitialize Agent

- **POST** `/agent/reinitialize`
- **Description**: Reinitialize the agent and LLM client
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Agent reinitialized successfully"
  }
  ```

## Available Tools

The assistant has access to several tools:

1. **get_weather** - Get current weather for a city
2. **get_date_time** - Get current date and time
3. **get_news** - Get latest news articles
4. **search_web** - Search the web using DuckDuckGo
5. **view_webpage** - View content of a webpage

## Python Client Usage

```python
from app.api.client import SmartHomeAPIClient

# Initialize client
client = SmartHomeAPIClient("http://localhost:8000")

# Check health
health = client.health_check()
print(health)

# Chat with the assistant
response = client.chat("What's the weather like today?")
print(response['response'])

# Direct LLM interaction
response = client.direct_llm_chat("Tell me a joke")
print(response['response'])

# Get available tools
tools = client.get_available_tools()
print(f"Available tools: {len(tools['tools'])}")
```

## JavaScript/Fetch Usage

```javascript
// Health check
const healthResponse = await fetch("http://localhost:8000/health");
const health = await healthResponse.json();
console.log(health);

// Chat
const chatResponse = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    message: "What's the weather like?",
    use_tools: true,
  }),
});
const chatData = await chatResponse.json();
console.log(chatData.response);
```

## cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is it?", "use_tools": true}'

# Direct LLM
curl -X POST http://localhost:8000/llm/direct \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# Get tools
curl http://localhost:8000/tools
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **422**: Validation Error (invalid request body)
- **500**: Internal Server Error

Error responses include details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Configuration

The API uses environment variables from `.env` file:

- `LLM_API_KEY` - API key for the LLM provider
- `LLM_MODEL` - Model name (e.g., "gpt-3.5-turbo")
- `LLM_API_ENDPOINT` - Custom API endpoint (optional)
- `WEATHER_API_KEY` - API key for weather service
- `NEWS_API_KEY` - API key for news service

## Development

### Running in Development Mode

The API server runs with auto-reload enabled, so changes to the code will automatically restart the server.

### Testing

Run the demo script to test all functionality:

```bash
python examples/api_demo.py
```

### Adding New Tools

1. Add your tool function to `app/tools/generic_tools.py`
2. Register it in `app/tools/tools.py`
3. The tool will automatically be available through the API

## CORS Support

The API includes CORS middleware configured to allow all origins for development. In production, you should configure specific allowed origins.

## Security Notes

- The API currently runs without authentication
- In production, consider adding API key authentication
- Configure CORS properly for production use
- Use HTTPS in production environments
