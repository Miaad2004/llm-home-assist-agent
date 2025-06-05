# Smart Home Assistant: Method Assignment Table

| File / Class / Method                        | Description / Responsibility                        | Assigned To |
|----------------------------------------------|-----------------------------------------------------|-------------|
| **app/ui/base.py**                          |                                                     |             |
| SmartHomeUIManager.send_text_command         | UI: Send text command to agent                      | Person A    |
| SmartHomeUIManager.start_voice_input         | UI: Start voice input                               | Person A    |
| SmartHomeUIManager.display_response          | UI: Display system message                          | Person A    |
| SmartHomeUIManager.update_device_status_ui   | UI: Update device status in UI                      | Person A    |
| **app/ui/ui_impl.py**                       |                                                     |             |
| SmartHomeUIManagerImpl.__init__              | UI: Initialize UI manager                           | Person A    |
| SmartHomeUIManagerImpl.send_text_command     | UI: Send text command to agent                      | Person A    |
| SmartHomeUIManagerImpl.start_voice_input     | UI: Start voice input                               | Person A    |
| SmartHomeUIManagerImpl.display_response      | UI: Display system message                          | Person A    |
| SmartHomeUIManagerImpl.update_device_status_ui| UI: Update device status in UI                      | Person A    |
| **app/agent/llm_client.py**                  |                                                     |             |
| LLMClientInterface.send_prompt               | LLM: Send prompt to LLM (UI/Voice)                  | Person A    |
| **app/agent/llm_client_impl.py**             |                                                     |             |
| GroqLLMClient.send_prompt                    | LLM: Groq API (UI LLM integration)                  | Person A    |
| TogetherAILLMClient.send_prompt              | LLM: TogetherAI API (Voice LLM integration)         | Person B    |
| **app/agent/agent_impl.py**                  |                                                     |             |
| DeviceCommandAgentImpl.__init__              | Agent: Initialize agent                             | Person A    |
| DeviceCommandAgentImpl.handle_user_input     | Agent: Handle user input (UI pipeline)              | Person A    |
| DeviceCommandAgentImpl.get_live_data         | Agent: Fetch live data (weather/news/time)          | Person B    |
| DeviceCommandAgentImpl.parse_llm_response    | Agent: Parse LLM response (voice pipeline)          | Person B    |
| DeviceCommandAgentImpl.call_device_function  | Agent: Call device function (hardware control)      | Person C    |
| **app/voice/tts_impl.py**                    |                                                     |             |
| TTSImpl.speak                               | Voice: Text-to-speech                               | Person B    |
| **app/voice/vad_wakeword.py**                |                                                     |             |
| VADWakeword.detect                          | Voice: Wake word detection                          | Person B    |
| **app/voice/whisper_stt.py**                 |                                                     |             |
| WhisperSTT.transcribe                       | Voice: Speech-to-text                               | Person B    |
| **app/devices/hardware.py**                  |                                                     |             |
| HardwareDeviceController.control_device      | Hardware: Control real device                       | Person C    |
| HardwareDeviceController.get_device_states   | Hardware: Get device states                         | Person C    |
| **app/devices/simulator.py**                 |                                                     |             |
| DeviceSimulator.control_device               | Hardware: Simulate device control                   | Person C    |
| DeviceSimulator.get_device_states            | Hardware: Get simulated device states               | Person C    |
| **app/data/news_api.py**                     |                                                     |             |
| NewsAPI.get_latest_headlines                 | Data: Fetch news headlines                          | Person B    |
| **app/data/weather_api.py**                  |                                                     |             |
| WeatherAPI.get_current_weather               | Data: Fetch weather                                 | Person B    |
| **app/data/time_utils.py**                   |                                                     |             |
| TimeUtils.get_current_time                   | Data: Get current time                              | Person A    |
| TimeUtils.get_current_date                   | Data: Get current date                              | Person A    |
