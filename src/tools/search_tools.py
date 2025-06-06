import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
from strands_agents.tools import tool
import structlog

logger = structlog.get_logger()


@tool
def web_search(query: str, num_results: int = 10) -> List[Dict[str, str]]:
    """
    Perform a web search using SerpAPI or a fallback search provider.
    
    Args:
        query: Search query string
        num_results: Number of results to return
        
    Returns:
        List of search results with title, link, and snippet
    """
    try:
        # For demo purposes, using a mock response
        # In production, integrate with SerpAPI or another search provider
        results = []
        for i in range(min(num_results, 5)):
            results.append({
                "title": f"Result {i+1} for: {query}",
                "link": f"https://example.com/result{i+1}",
                "snippet": f"This is a sample snippet for search result {i+1} related to {query}",
                "source": "mock_search"
            })
        
        logger.info("Web search completed", query=query, num_results=len(results))
        return results
        
    except Exception as e:
        logger.error("Web search failed", query=query, error=str(e))
        raise


@tool
def fetch_webpage_content(url: str) -> Dict[str, Any]:
    """
    Fetch and parse content from a webpage.
    
    Args:
        url: URL to fetch
        
    Returns:
        Dictionary with page content, metadata, and extracted text
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract metadata
        title = soup.find('title')
        title_text = title.text.strip() if title else ""
        
        # Extract main content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                "text": link.text.strip(),
                "url": link['href']
            })
        
        result = {
            "url": url,
            "title": title_text,
            "content": text[:5000],  # Limit content length
            "links": links[:20],  # Limit number of links
            "fetch_time": datetime.now().isoformat()
        }
        
        logger.info("Webpage fetched", url=url, title=title_text)
        return result
        
    except Exception as e:
        logger.error("Failed to fetch webpage", url=url, error=str(e))
        raise


@tool
async def fetch_multiple_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch content from multiple URLs concurrently.
    
    Args:
        urls: List of URLs to fetch
        
    Returns:
        List of fetched content dictionaries
    """
    async def fetch_url(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                text = await response.text()
                
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.find('title')
                title_text = title.text.strip() if title else ""
                
                # Simple text extraction
                for script in soup(["script", "style"]):
                    script.decompose()
                
                content = soup.get_text()
                content = ' '.join(content.split())[:5000]
                
                return {
                    "url": url,
                    "title": title_text,
                    "content": content,
                    "status": response.status,
                    "success": True
                }
                
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }
    
    async def fetch_all():
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url) for url in urls]
            return await asyncio.gather(*tasks)
    
    try:
        results = await fetch_all()
        
        successful = sum(1 for r in results if r.get("success", False))
        logger.info(
            "Multiple URLs fetched",
            total=len(urls),
            successful=successful
        )
        
        return results
        
    except Exception as e:
        logger.error("Failed to fetch multiple URLs", error=str(e))
        raise


@tool
def search_academic_papers(
    query: str,
    source: str = "arxiv",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for academic papers from various sources.
    
    Args:
        query: Search query
        source: Paper source (arxiv, pubmed, semantic_scholar)
        max_results: Maximum number of results
        
    Returns:
        List of paper metadata
    """
    try:
        papers = []
        
        if source == "arxiv":
            # Mock arXiv search results
            for i in range(min(max_results, 5)):
                papers.append({
                    "title": f"Paper {i+1}: {query} in Machine Learning",
                    "authors": [f"Author {j+1}" for j in range(3)],
                    "abstract": f"This paper discusses {query} in the context of ML...",
                    "url": f"https://arxiv.org/abs/2024.{1000+i}",
                    "published": "2024-01-01",
                    "source": "arxiv"
                })
        
        logger.info(
            "Academic paper search completed",
            query=query,
            source=source,
            results=len(papers)
        )
        
        return papers
        
    except Exception as e:
        logger.error("Academic paper search failed", error=str(e))
        raise


@tool
def extract_structured_data(
    html_content: str,
    selectors: Dict[str, str]
) -> Dict[str, Any]:
    """
    Extract structured data from HTML using CSS selectors.
    
    Args:
        html_content: HTML content to parse
        selectors: Dictionary mapping field names to CSS selectors
        
    Returns:
        Dictionary of extracted data
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_data = {}
        
        for field_name, selector in selectors.items():
            elements = soup.select(selector)
            
            if len(elements) == 0:
                extracted_data[field_name] = None
            elif len(elements) == 1:
                extracted_data[field_name] = elements[0].get_text(strip=True)
            else:
                extracted_data[field_name] = [
                    elem.get_text(strip=True) for elem in elements
                ]
        
        logger.info(
            "Structured data extracted",
            fields=list(extracted_data.keys())
        )
        
        return extracted_data
        
    except Exception as e:
        logger.error("Failed to extract structured data", error=str(e))
        raise


@tool
def search_company_info(company_name: str) -> Dict[str, Any]:
    """
    Search for company information from various sources.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Dictionary with company information
    """
    try:
        # Mock company information
        info = {
            "name": company_name,
            "industry": "Technology",
            "founded": "2010",
            "headquarters": "San Francisco, CA",
            "employees": "1000-5000",
            "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
            "description": f"{company_name} is a leading technology company...",
            "recent_news": [
                {
                    "title": f"{company_name} Announces Q4 Results",
                    "date": "2024-01-15",
                    "summary": "Strong growth in cloud services..."
                }
            ],
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "data_source": "mock_data"
        }
        
        logger.info("Company info searched", company=company_name)
        return info
        
    except Exception as e:
        logger.error("Company search failed", company=company_name, error=str(e))
        raise


@tool
def verify_facts(
    claims: List[str],
    sources: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Verify facts and claims against reliable sources.
    
    Args:
        claims: List of claims to verify
        sources: Optional list of specific sources to check
        
    Returns:
        List of verification results
    """
    try:
        results = []
        
        for claim in claims:
            # Mock fact verification
            result = {
                "claim": claim,
                "verdict": "partially_true",
                "confidence": 0.75,
                "supporting_sources": [
                    {
                        "url": "https://example.com/source1",
                        "title": "Supporting Evidence",
                        "relevance": 0.8
                    }
                ],
                "contradicting_sources": [],
                "explanation": f"The claim '{claim}' is partially supported by evidence..."
            }
            results.append(result)
        
        logger.info("Fact verification completed", num_claims=len(claims))
        return results
        
    except Exception as e:
        logger.error("Fact verification failed", error=str(e))
        raise