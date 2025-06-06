import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Optional, Any, Union
from config.settings import Settings


class WebViewer:
    """
    Fetches and parses web page content for the agent to view websites.
    """

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    @staticmethod
    def view_webpage(url: str, max_content_length: int = 5000) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """
        Fetches and parses a webpage, extracting title, main content, and links.
        Args:
            url (str): The URL of the webpage to fetch.
            max_content_length (int): Maximum length of the content to return.

        Returns:
            Dict[str, Union[str, List[Dict[str, str]]]]: A dictionary containing the title, content, URL, links, and status.
        """
        if Settings.VERBOSE_LEVEL > 1:
            print("WebViewer.view_webpage called with URL:", url)

        try:
            response = WebViewer.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract main content
            content = WebViewer._extract_main_content(soup)

            # Clean and truncate content
            content = WebViewer._clean_text(content)
            if len(content) > max_content_length:
                content = content[:max_content_length] + "... [Content truncated]"

            # Extract links
            links = WebViewer._extract_links(soup, url)

            return {
                'title': title_text,
                'content': content,
                'url': url,
                'links': links[:10],  # Limit to first 10 links
                'status': 'success'
            }

        except requests.exceptions.RequestException as e:
            return {
                'title': '',
                'content': f'Error fetching webpage: {str(e)}',
                'url': url,
                'links': [],
                'status': 'error'
            }
        except Exception as e:
            return {
                'title': '',
                'content': f'Error parsing webpage: {str(e)}',
                'url': url,
                'links': [],
                'status': 'error'
            }

    @staticmethod
    def _extract_main_content(soup: BeautifulSoup) -> str:
        """Extract the main content from the webpage."""
        main_selectors = [
            'main', 'article', '.content', '#content',
            '.main-content', '#main-content', '.post-content',
            '.article-body', '.entry-content'
        ]

        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                return main_content.get_text()

        body = soup.find('body')
        if body:
            return body.get_text()

        return soup.get_text()

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text content."""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    @staticmethod
    def _extract_links(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links from the webpage."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()

            if text and href:
                absolute_url = urljoin(base_url, href)
                if absolute_url.startswith(('http://', 'https://')):
                    links.append({
                        'text': text[:100],
                        'url': absolute_url
                    })

        return links