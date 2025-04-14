"""
News Fetcher Tool for the Personal AI Agent System.

This module provides functionality to fetch recent news articles
based on topics, keywords, or sources.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logger = logging.getLogger("news_fetcher")

def run(
    query: str,
    max_results: int = 5,
    days_back: int = 7,
    sources: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    language: str = "en",
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["news", "research"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Fetch recent news articles based on the provided query and filters.
    
    Args:
        query: The search query string for news articles
        max_results: Maximum number of news articles to return (default: 5)
        days_back: How many days back to search for news (default: 7)
        sources: Optional list of news sources to include
        categories: Optional list of news categories (e.g., "business", "technology")
        language: Language code for the news articles (default: "en" for English)
        store_memory: Whether to store the news results in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing news articles and metadata
    """
    logger.info(f"Fetching news for query: {query}, days_back: {days_back}")
    
    # In a real implementation, this would use an actual news API like NewsAPI or GDELT
    # For now, we'll simulate the news results
    
    try:
        # Simulate API call delay and processing
        articles = _simulate_news_results(query, max_results, days_back, sources, categories)
        
        news_result = {
            "success": True,
            "query": query,
            "days_back": days_back,
            "language": language,
            "num_results": len(articles),
            "articles": articles
        }
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                memory_entry = {
                    "type": "news_fetch",
                    "query": query,
                    "timeframe": f"Past {days_back} days",
                    "results_summary": f"Found {len(articles)} news articles for '{query}'",
                    "top_headlines": [article["title"] for article in articles[:3]]  # Store only top 3 headlines
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored news fetch results in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store news in memory: {str(e)}")
        
        return news_result
    except Exception as e:
        error_msg = f"Error fetching news: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "query": query
        }

def _simulate_news_results(
    query: str, 
    max_results: int, 
    days_back: int,
    sources: Optional[List[str]],
    categories: Optional[List[str]]
) -> List[Dict[str, Any]]:
    """
    Simulate news results for development purposes.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return
        days_back: How many days back to search
        sources: Optional list of news sources to include
        categories: Optional list of news categories
        
    Returns:
        List of simulated news articles
    """
    # Get current date for generating realistic publication dates
    today = datetime.datetime.now()
    
    # Sample news sources
    all_sources = ["CNN", "BBC", "Reuters", "Associated Press", "The New York Times", 
                  "The Washington Post", "The Guardian", "Bloomberg", "CNBC", "TechCrunch"]
    
    # Filter sources if specified
    if sources:
        news_sources = [s for s in all_sources if s in sources]
    else:
        news_sources = all_sources
    
    # Sample news articles
    sample_articles = []
    
    for i in range(max_results * 2):  # Generate more than needed to allow for filtering
        # Generate a random date within the specified range
        days_offset = i % days_back
        pub_date = today - datetime.timedelta(days=days_offset)
        
        # Assign a source
        source = news_sources[i % len(news_sources)]
        
        # Generate article data
        article = {
            "title": f"Latest Developments in {query}: What You Need to Know" if i == 0 else
                     f"{query} Shows Promising Results in Recent Study" if i == 1 else
                     f"Experts Weigh In on the Future of {query}" if i == 2 else
                     f"The Impact of {query} on Global Markets" if i == 3 else
                     f"New Breakthrough in {query} Research Announced" if i == 4 else
                     f"{query}: A Comprehensive Analysis" if i == 5 else
                     f"Understanding the Implications of Recent {query} Developments" if i == 6 else
                     f"{query} in 2025: Trends and Predictions",
            "source": source,
            "author": f"John Doe" if i % 3 == 0 else f"Jane Smith" if i % 3 == 1 else "Alex Johnson",
            "published_date": pub_date.strftime("%Y-%m-%d %H:%M:%S"),
            "url": f"https://{source.lower().replace(' ', '')}.com/news/{query.replace(' ', '-')}-{i}",
            "snippet": f"Recent developments in {query} have shown significant progress, according to experts in the field. "
                      f"This article explores the latest findings and their implications for the future.",
            "category": "Technology" if i % 4 == 0 else 
                        "Business" if i % 4 == 1 else 
                        "Science" if i % 4 == 2 else 
                        "World"
        }
        
        sample_articles.append(article)
    
    # Apply category filtering if specified
    if categories:
        filtered_articles = [
            article for article in sample_articles 
            if article["category"].lower() in [cat.lower() for cat in categories]
        ]
        articles = filtered_articles if filtered_articles else sample_articles[:max_results]
    else:
        articles = sample_articles
    
    # Limit to requested number of results
    return articles[:min(max_results, len(articles))]
