from .generic_tools import GenericTools, device_controller
from .web_viewer import WebViewer


TOOLS = {
    "get_weather": {
        "description": "Get the current weather for a specified city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city to get the weather for."
                }
            },
            "required": ["city"]
        },
        "function_docstring": GenericTools.get_weather_and_aqi.__doc__,
        "function": GenericTools.get_weather_and_aqi
    },
    
    "get_date_time": {
        "description": "Get the current date and time.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "function_docstring": GenericTools.get_date_time.__doc__,
        "function": GenericTools.get_date_time
    },
    
    "get_news": {
        "description": "Get the latest news articles related to a specified query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for news articles."
                }
            },
            "required": ["query"]
        },
        "function_docstring": GenericTools.get_news.__doc__,
        "function": GenericTools.get_news
    },
    
    "view_webpage": {
        "description": "Visit and view the content of a webpage by URL. Can open links and browse websites to extract text content, headers, and other relevant information.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the webpage to view."
                }
            },
            "required": ["url"]
        },
        "function_docstring": WebViewer.view_webpage.__doc__,
        "function": WebViewer.view_webpage
    },
    
    "search_web": {
        "description": "Search the web for a specified query using DuckDuckGo.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to use."
                }
            },
            "required": ["query"]
        },
        "function_docstring": GenericTools.search_web.__doc__,
        "function": GenericTools.search_web
    },
    
    # Device control tools
    "get_devices": {
        "description": "Get a list of all available smart home devices and their current status.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "function_docstring": GenericTools.get_devices.__doc__,
        "function": GenericTools.get_devices
    },
    
    "control_device": {
        "description": "Control a smart home device by turning it on or off.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "ID of the device to control (e.g., 'bedroom_light', 'living_lamp')."
                },
                "action": {
                    "type": "string",
                    "enum": ["on", "off"],
                    "description": "Action to perform on the device, either 'on' or 'off'."
                }
            },
            "required": ["device_id", "action"]
        },
        "function_docstring": GenericTools.control_device.__doc__,
        "function": GenericTools.control_device
    }
}
