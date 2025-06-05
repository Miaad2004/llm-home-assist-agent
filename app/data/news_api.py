class NewsAPI:
    """
    Fetches latest news headlines from an external API.
    """
    def get_latest_headlines(self, count: int = 3) -> list[str]:
        """
        Input: count (int) — Number of headlines to fetch
        Output: list[str] — List of news headlines
        Action: Query news API and return headlines
        """
        # TODO: Implement real API call
        return [f"Sample headline {i+1}" for i in range(count)]
