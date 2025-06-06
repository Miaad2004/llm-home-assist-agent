import unittest
from unittest.mock import MagicMock, patch
from app.agent.agent_impl import DeviceCommandAgentImpl
from app.devices.simulator import DeviceSimulator

class TestDeviceCommandAgent(unittest.TestCase):
    
    def setUp(self):
        # Create a mock LLM client
        self.mock_llm = MagicMock()
        self.device_sim = DeviceSimulator()
        self.agent = DeviceCommandAgentImpl(self.mock_llm, self.device_sim)
        
    def test_parse_llm_response(self):
        """Test parsing LLM responses into commands"""
        # Test with markdown JSON format
        markdown_response = """
        Here's the command:
        ```json
        {
          "device": "light",
          "location": "living room",
          "action": "on",
          "value": ""
        }
        ```
        """
        expected = {
            "device": "light",
            "location": "living room",
            "action": "on",
            "value": ""
        }
        result = self.agent.parse_llm_response(markdown_response)
        self.assertEqual(result, expected)
        
        # Test with plain JSON format
        plain_response = """I understood this as: {"device": "ac", "location": "bedroom", "action": "set", "value": "24"}"""
        expected = {
            "device": "ac",
            "location": "bedroom",
            "action": "set",
            "value": "24"
        }
        result = self.agent.parse_llm_response(plain_response)
        self.assertEqual(result, expected)
        
        # Test with invalid format
        invalid_response = "I don't know what to do with this request."
        result = self.agent.parse_llm_response(invalid_response)
        self.assertEqual(result, {})
    
    def test_weather_request(self):
        """Test handling weather requests"""
        with patch.object(self.agent.weather_api, 'get_current_weather', return_value="Sunny, 24°C"):
            result = self.agent.handle_user_input("What's the weather like?")
            self.assertIn("Current weather", result)
            self.assertIn("Sunny, 24°C", result)
    
    def test_news_request(self):
        """Test handling news requests"""
        with patch.object(self.agent.news_api, 'get_latest_headlines', return_value=["Headline 1", "Headline 2"]):
            result = self.agent.handle_user_input("Give me the latest news")
            self.assertIn("Latest headlines", result)
            self.assertIn("Headline 1", result)
            self.assertIn("Headline 2", result)
    
    def test_time_request(self):
        """Test handling time requests"""
        with patch.object(self.agent.time_utils, 'get_current_time', return_value="3:30 PM"):
            with patch.object(self.agent.time_utils, 'get_current_date', return_value="2025-06-06"):
                result = self.agent.handle_user_input("What time is it?")
                self.assertIn("The time is 3:30 PM", result)
                self.assertIn("2025-06-06", result)
    
    def test_device_command(self):
        """Test handling device commands"""
        # Mock LLM to return a specific response
        self.mock_llm.send_prompt.return_value = """
        ```json
        {
          "device": "light",
          "location": "bedroom",
          "action": "on",
          "value": ""
        }
        ```
        """
        
        result = self.agent.handle_user_input("Turn on the bedroom light")
        self.assertIn("Light in bedroom turned on", result)

if __name__ == "__main__":
    unittest.main()