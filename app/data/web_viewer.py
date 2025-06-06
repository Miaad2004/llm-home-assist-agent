# filepath: d:\Uni\Term_6\DM\Agent\smart-home-assistant\app\data\web_viewer.py
# Assigned to: Person B (Data pipeline)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Optional, Any, Union

class WebViewer:
    """
    Fetches and parses web page content for the agent to view websites.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def view_webpage(self, url: str, max_content_length: int = 5000) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """
        Input: url (str) — URL of the webpage to view
               max_content_length (int) — Maximum length of content to extract
        Output: Dict[str, str] — Dictionary containing title, content, and metadata
        Calls: HTTP requests to fetch webpage
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Clean and truncate content
            content = self._clean_text(content)
            if len(content) > max_content_length:
                content = content[:max_content_length] + "... [Content truncated]"
            
            # Extract links
            links = self._extract_links(soup, url)
            
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
        except Exception as e:            return {
                'title': '',
                'content': f'Error parsing webpage: {str(e)}',
                'url': url,
                'links': [],
                'status': 'error'
            }
    
    def get_page_summary(self, url: str) -> str:
        """
        Input: url (str) — URL of the webpage to summarize
        Output: str — Brief summary of the webpage content
        Calls: view_webpage method
        """
        page_data = self.view_webpage(url, max_content_length=2000)
        
        if page_data['status'] == 'error':
            return f"Could not access {url}: {page_data['content']}"
        
        title = page_data['title']
        content = str(page_data['content'])  # Ensure content is a string
        
        # Create a brief summary
        summary = f"**{title}**\n\n"
        
        # Get first few paragraphs or sentences
        sentences = content.split('. ')
        summary_sentences = sentences[:3]  # First 3 sentences
        summary += '. '.join(summary_sentences)
        
        if len(sentences) > 3:
            summary += "..."
        
        return summary
    
    def search_in_page(self, url: str, search_term: str) -> Dict[str, Any]:
        """
        Input: url (str) — URL of the webpage to search
               search_term (str) — Term to search for in the page
        Output: Dict — Search results with matches and context
        Calls: view_webpage method
        """
        page_data = self.view_webpage(url)
        
        if page_data['status'] == 'error':
            return {
                'found': False,
                'matches': 0,
                'contexts': [],
                'error': page_data['content']
            }
        content = page_data['content'].lower()
        search_term_lower = search_term.lower()
        
        # Ensure content is a string
        if isinstance(content, list):
            content = str(page_data['content']).lower()
        else:
            content = str(content)
        
        # Find all matches
        matches = []
        start = 0
        while True:
            pos = content.find(search_term_lower, start)
            if pos == -1:
                break
            matches.append(pos)
            start = pos + 1
        
        # Extract context around matches
        contexts = []
        for match_pos in matches[:5]:  # Limit to first 5 matches
            start_context = max(0, match_pos - 100)
            end_context = min(len(content), match_pos + len(search_term) + 100)
            context = page_data['content'][start_context:end_context]
            contexts.append(f"...{context}...")
        
        return {
            'found': len(matches) > 0,
            'matches': len(matches),
            'contexts': contexts,
            'title': page_data['title']
        }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from the webpage."""
        # Try to find main content areas
        main_selectors = [
            'main', 'article', '.content', '#content', 
            '.main-content', '#main-content', '.post-content',
            '.article-body', '.entry-content'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                return main_content.get_text()
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text()
        
        return soup.get_text()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links from the webpage."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            if text and href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                # Filter out non-http links
                if absolute_url.startswith(('http://', 'https://')):
                    links.append({
                        'text': text[:100],  # Limit text length
                        'url': absolute_url
                    })
        
        return links