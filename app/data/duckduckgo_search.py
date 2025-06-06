from duckduckgo_search import DDGS

class DuckDuckGoSearch:
    """
    Provides web search using the duckduckgo-search library.
    """
    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Input: query (str) — Search query
        Output: list[dict] — List of search results (title, href, body)
        Calls: duckduckgo-search
        """
        ddgs = DDGS()
        results = []
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                'title': r.get('title'),
                'href': r.get('href'),
                'body': r.get('body')
            })
        return results