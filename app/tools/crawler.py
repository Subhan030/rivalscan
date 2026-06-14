from typing import List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import httpx

def crawl_domain(start_url: str, max_pages: int = 10) -> List[str]:
    visited = set()
    to_visit = [start_url]
    domain = urlparse(start_url).netloc
    discovered_urls = []
    
    with httpx.Client(timeout=5.0) as client:
        while to_visit and len(discovered_urls) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            
            visited.add(url)
            discovered_urls.append(url)
            
            try:
                response = client.get(url)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, str(link['href']))
                    next_domain = urlparse(next_url).netloc
                    
                    if next_domain == domain and next_url not in visited:
                        to_visit.append(next_url)
            except Exception:
                pass
                
    return discovered_urls
