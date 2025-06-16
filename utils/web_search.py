from duckduckgo_search.duckduckgo_search import DDGS
import logging

def duckduckgo_search(query: str, max_results: int = 5):
    """
    Perform a DuckDuckGo search and return top results.

    :param query: Search query string.
    :param max_results: Max number of results to return.
    :return: List of dicts with 'title', 'url', 'snippet'.
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
        if not results:
            return []
        # Return list of relevant info for display
        return [{
            "title": r.get("title"),
            "url": r.get("href"),
            "snippet": r.get("body")
        } for r in results]
    except Exception as e:
        logging.error(f"DuckDuckGo search failed for query '{query}': {e}")
        return []
