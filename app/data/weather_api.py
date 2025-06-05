# Assigned to: Person B (Data pipeline)
class WeatherAPI:
    """
    Fetches current weather information from an external API.
    """
    def get_current_weather(self, location: str = "local") -> str:
        """
        Input: location (str) — Location to fetch weather for
        Output: str — Weather summary (e.g., "Sunny, 24°C")
        Calls: Weather API
        """
        # TODO: Implement real API call
        return f"Sample weather for {location}: Sunny, 24°C"
