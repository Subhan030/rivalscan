import httpx
from typing import List, Dict
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    if not settings.search_api_key:
        return [{"title": f"Mock Title for {query}", "url": "https://example.com", "snippet": "Mock snippet"}]
    
    url = "https://google.serper.dev/search"
    payload = {"q": query, "num": num_results}
    headers = {
        'X-API-KEY': settings.search_api_key,
        'Content-Type': 'application/json'
    }
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        return results
