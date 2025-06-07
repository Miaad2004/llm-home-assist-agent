import datetime
import json
from config.settings import Settings
from urllib.parse import urljoin
import requests
from duckduckgo_search import DDGS

device_controller = None

class GenericTools:
    @staticmethod
    def get_date_time() -> str:
        """
        Returns the current date and time in ISO format.
        Args:
            None
        
        Returns:
            str: Current date and time in ISO format (e.g., "2023-10-01T12:00:00")
        
        Example call:
        {
            "Question": "What is the time?",
            "Thought": "The user wants to know the current time. I must use the get_date_time tool to provide the answer.",
            "tools_used": ["get_date_time"],
            "Answer": "The current date and time is 2023-10-01T12:00:00. Or anything similar."
        }
        """
        if Settings.VERBOSE_LEVEL > 1:
            print("GenericTools.get_date_time called")
        
        return datetime.datetime.now().isoformat()
    
    @staticmethod
    def get_weather_and_aqi(city: str) -> str:
        """
        Returns a mock weather report for the specified city.
        Args:
            city (str): Name of the city to get the weather for
        
        Returns:
            str: Weather report in JSON format, including temperature, humidity, and AQI.
        
        Example call:
        {
            "Question": "What is the weather in New York?",
            "Thought": "The user wants to know the current weather in New York. I must use the get_weather_and_aqi tool to provide the answer.",
            "tools_used": ["get_weather_and_aqi"],
            "Answer": "The current weather in New York is 20°C with 60% humidity ..... how ever u like it"
        }
        """
        
        if Settings.VERBOSE_LEVEL > 1:
            print("GenericTools.get_weather_and_aqi called with city:", city)
        print("Using Weather API endpoint:", Settings.WEATHER_API_ENDPOINT)
        end_point = urljoin(Settings.WEATHER_API_ENDPOINT,
                            "current.json?key={}&q={}&aqi=yes".format(Settings().WEATHER_API_KEY, city))
        
        print("Weather API endpoint:", end_point)
        output = "Failed to get weather data"
        try:
            response = requests.get(end_point)
            if response.status_code == 200:
                data = response.json()
                output = str(data)
            
            else:
                print(f"Error fetching weather data: {response.status_code} - {response.text}")
                output += f" \n Error: {response.status_code} - {response.text}"
                
                
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            pass
        
        return output
    
    @staticmethod
    def get_news(query: str) -> str:
        """
        Returns the latest news articles related to the specified query.
        Args:
            query (str): Search query for news articles
        Returns:
            str: News articles in JSON format, including title, description, and URL.
        Example call:
        {
            "Question": "What is the latest news on AI?",
            "Thought": "The user wants to know the latest news on AI. I must use the get_news tool to provide the answer.",
            "tools_used": ["get_news"],
            "Answer": "Here are the latest news articles on AI: [Title: AI Breakthrough, Description: A new AI model has been released, URL: http://example.com/news/ai-breakthrough]. Or anything similar."
        }
        """
        
        if Settings.VERBOSE_LEVEL > 1:
            print("GenericTools.get_news called with query:", query)
        
        endpoint = urljoin(Settings.NEWS_API_ENDPOINT, 
                           "/v2/everything?q={}&apiKey={}&sortBy=relevancy&pageSize=5".format(query, Settings().NEWS_API_KEY))
        output = "Failed to get news data"
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                # Process data to reduce size - only keep essential information for 5 articles
                processed_articles = []
                for article in data.get('articles', [])[:5]:  # Limit to 5 articles
                    processed_articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', '')[:200],  # Truncate description
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', '')
                    })
                output = json.dumps({'articles': processed_articles})
                
        except requests.RequestException as e:
            print(f"Error fetching news data: {e}")
            output = f"Failed to get news data: {str(e)}"
        
        return output
    
    @staticmethod
    def get_url_content(url: str) -> str:
        """
        Fetches the content of a given URL.
        Args:
            url (str): The URL to fetch content from.
        
        Returns:
            str: The content of the URL or an error message if the request fails.
        
        Example call:
        {
            "Question": "What is the content of https://example.com?",
            "Thought": "The user wants to know the content of a specific URL. I must use the get_url_content tool to provide the answer.",
            "tools_used": ["get_url_content"],
            "Answer": "The content of https://example.com is: [content here]. Or anything similar."
        }
        """
        
        if Settings.VERBOSE_LEVEL > 1:
            print("GenericTools.get_url_content called with URL:", url)
        
        output = "Failed to fetch URL content"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                output = response.text
                
        except requests.RequestException as e:
            print(f"Error fetching URL content: {e}")
        
        return output
    
    
    @staticmethod
    def search_web(query: str) -> str:
        """
        Searches the web for the given query using DuckDuckGo and returns a list of results.
        You can use other tools to view one of the results using the URL.
        Args:
            query (str): The search query to use.
        
        Returns:
            str: A string representation of the search results, including titles, URLs, and snippets.
            
        Example call:
        {
            "Question": "Is there a new Harry Potter book?",
            "Thought": "The user wants to search the web for information about a new Harry Potter book. I must use the search_web tool to provide the answer.",
            "tools_used": ["search_web"],
            "Answer": "No new Harry Potter book has been announced."
        }
        
        """
        
        if Settings.VERBOSE_LEVEL > 1:
            print("GenericTools.search_web called with query:", query)
        
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            output = []
            for result in results:
                output.append({
                    'title': result['title'],
                    'url': result['href'],
                    'snippet': result['body']
                })
            return str(output)
    
    @staticmethod
    def get_devices() -> str:
        """
        Returns a list of all available smart home devices and their current status.
        
        Args:
            None
            
        Returns:
            str: JSON string containing all devices with their properties (id, name, type, location, status)
        
        Example call:
        {
            "Question": "What devices can I control?",
            "Thought": "The user wants to know what smart devices are available. I must use the get_devices tool to provide this information.",
            "tools_used": ["get_devices"],
            "Answer": "You have several devices in your home that I can control: 
                      1. A bedroom light (currently off)
                      2. A living room lamp (currently on)
                      3. Kitchen light (currently off)
                      4. Bedroom AC (currently off)
                      5. Living room TV (currently off)"
        }
        """
        global device_controller
        
        if Settings.VERBOSE_LEVEL > 1:
            print("GenericTools.get_devices called")
        
        if not device_controller:
            return "Error: Device controller is not initialized"
        
        try:
            # Get devices from controller
            devices = device_controller.get_device_states()
            
            # Format for better readability
            formatted_devices = []
            
            if isinstance(devices, dict):
                # Convert dictionary to list
                for device_id, device_data in devices.items():
                    formatted_devices.append(device_data)
            else:
                # Already a list
                formatted_devices = devices
                
            # Convert to JSON string
            return json.dumps(formatted_devices, indent=2)
        except Exception as e:
            return f"Error retrieving devices: {str(e)}"
    
    @staticmethod
    def control_device(device_id: str, action: str) -> str:
        """
        Controls a specific smart home device, turning it on or off.
        
        Args:
            device_id (str): The ID of the device to control (e.g., "bedroom_light", "living_lamp")
            action (str): The action to perform, must be either "on" or "off"
            
        Returns:
            str: Result of the control operation
        
        Example call:
        {
            "Question": "Turn on the bedroom light",
            "Thought": "The user wants to turn on the bedroom light. I need to use the control_device tool with the bedroom light ID.",
            "tools_used": ["control_device"],
            "Answer": "I've turned on the bedroom light for you."
        }
        """
        global device_controller
        
        if Settings.VERBOSE_LEVEL > 1:
            print(f"GenericTools.control_device called with device_id={device_id}, action={action}")
        
        if not device_controller:
            return "Error: Device controller is not initialized"
        
        # Validate action
        if action not in ["on", "off"]:
            return "Error: Action must be 'on' or 'off'"
        
        try:
            # Send command to device controller
            result = device_controller.control_device({
                "device_id": device_id,
                "action": action
            })
            
            return result
        except Exception as e:
            return f"Error controlling device: {str(e)}"



