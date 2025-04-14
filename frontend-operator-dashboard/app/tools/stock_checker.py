"""
Stock Checker Tool for the Personal AI Agent System.

This module provides functionality to retrieve stock market data,
including current prices, historical data, and company information.
"""

import os
import json
import time
import random
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("stock_checker")

def run(
    symbol: str,
    query_type: str = "quote",
    interval: str = "1d",
    period: str = "1mo",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_news: bool = False,
    include_fundamentals: bool = False,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["stock", "finance"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Retrieve stock market data for a specified symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., "AAPL", "MSFT")
        query_type: Type of data to retrieve (quote, historical, company)
        interval: Data interval for historical data (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
        period: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        start_date: Start date for historical data (YYYY-MM-DD)
        end_date: End date for historical data (YYYY-MM-DD)
        include_news: Whether to include recent news articles
        include_fundamentals: Whether to include fundamental company data
        store_memory: Whether to store the stock data in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing stock market data
    """
    logger.info(f"Retrieving {query_type} stock data for {symbol}")
    
    try:
        # Validate inputs
        if not symbol:
            raise ValueError("Stock symbol is required")
            
        if query_type not in ["quote", "historical", "company"]:
            raise ValueError(f"Invalid query type: {query_type}. Supported types: quote, historical, company")
            
        if interval not in ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]:
            raise ValueError(f"Invalid interval: {interval}. Supported intervals: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo")
            
        if period not in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
            raise ValueError(f"Invalid period: {period}. Supported periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
            
        if query_type == "historical" and start_date and end_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD format.")
        
        # In a real implementation, this would use a stock market API
        # For now, we'll simulate the stock data
        
        # Simulate stock data retrieval
        if query_type == "quote":
            stock_data = _simulate_stock_quote(symbol)
        elif query_type == "historical":
            stock_data = _simulate_historical_stock_data(symbol, interval, period, start_date, end_date)
        else:  # company
            stock_data = _simulate_company_info(symbol)
        
        # Add news if requested
        if include_news:
            stock_data["news"] = _simulate_stock_news(symbol)
        
        # Add fundamentals if requested
        if include_fundamentals:
            stock_data["fundamentals"] = _simulate_stock_fundamentals(symbol)
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a summary of the stock data for memory storage
                if query_type == "quote":
                    summary = f"{symbol} current price: ${stock_data['price']:.2f}, change: {stock_data['change']:.2f} ({stock_data['change_percent']:.2f}%)"
                elif query_type == "historical":
                    summary = f"Historical stock data for {symbol} ({interval} interval, {period} period)"
                else:  # company
                    summary = f"Company information for {symbol} ({stock_data['company_name']})"
                
                memory_entry = {
                    "type": "stock_data",
                    "symbol": symbol,
                    "query_type": query_type,
                    "summary": summary,
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + [symbol.lower()]
                )
                
                logger.info(f"Stored stock data in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store stock data in memory: {str(e)}")
        
        return {
            "success": True,
            "symbol": symbol,
            "query_type": query_type,
            "data": stock_data
        }
    except Exception as e:
        error_msg = f"Error retrieving stock data: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "symbol": symbol,
            "query_type": query_type
        }

def _simulate_stock_quote(symbol: str) -> Dict[str, Any]:
    """
    Simulate current stock quote data.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary with simulated stock quote data
    """
    # Generate a deterministic but seemingly random price based on symbol
    symbol_hash = sum(ord(c) for c in symbol)
    random.seed(symbol_hash + int(time.time() / 3600))  # Change seed hourly
    
    # Base price between $10 and $500
    base_price = 10 + (symbol_hash % 490)
    
    # Add some randomness
    price = round(base_price * (1 + random.uniform(-0.05, 0.05)), 2)
    
    # Generate previous close (slightly different from current price)
    prev_close = round(price * (1 + random.uniform(-0.03, 0.03)), 2)
    
    # Calculate change and change percent
    change = round(price - prev_close, 2)
    change_percent = round((change / prev_close) * 100, 2)
    
    # Generate other data
    volume = random.randint(100000, 10000000)
    avg_volume = volume * random.uniform(0.8, 1.2)
    market_cap = price * random.randint(1000000, 1000000000)
    
    # Generate high, low, open
    if change > 0:
        day_high = round(price * (1 + random.uniform(0, 0.02)), 2)
        day_low = round(prev_close * (1 - random.uniform(0, 0.02)), 2)
        day_open = round(prev_close * (1 + random.uniform(0, 0.01)), 2)
    else:
        day_high = round(prev_close * (1 + random.uniform(0, 0.02)), 2)
        day_low = round(price * (1 - random.uniform(0, 0.02)), 2)
        day_open = round(prev_close * (1 - random.uniform(0, 0.01)), 2)
    
    # Generate 52-week high and low
    week_52_high = round(price * (1 + random.uniform(0.05, 0.3)), 2)
    week_52_low = round(price * (1 - random.uniform(0.05, 0.3)), 2)
    
    # Generate company name based on symbol
    company_name = _get_company_name(symbol)
    
    return {
        "symbol": symbol,
        "company_name": company_name,
        "price": price,
        "currency": "USD",
        "change": change,
        "change_percent": change_percent,
        "prev_close": prev_close,
        "open": day_open,
        "day_high": day_high,
        "day_low": day_low,
        "volume": volume,
        "avg_volume": int(avg_volume),
        "market_cap": market_cap,
        "pe_ratio": round(random.uniform(5, 50), 2),
        "dividend_yield": round(random.uniform(0, 5), 2),
        "52_week_high": week_52_high,
        "52_week_low": week_52_low,
        "timestamp": datetime.now().isoformat()
    }

def _simulate_historical_stock_data(
    symbol: str,
    interval: str,
    period: str,
    start_date: Optional[str],
    end_date: Optional[str]
) -> Dict[str, Any]:
    """
    Simulate historical stock data.
    
    Args:
        symbol: Stock ticker symbol
        interval: Data interval
        period: Time period
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with simulated historical stock data
    """
    # Determine date range
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = datetime.now()
        
        if period == "1d":
            start = end - timedelta(days=1)
        elif period == "5d":
            start = end - timedelta(days=5)
        elif period == "1mo":
            start = end - timedelta(days=30)
        elif period == "3mo":
            start = end - timedelta(days=90)
        elif period == "6mo":
            start = end - timedelta(days=180)
        elif period == "1y":
            start = end - timedelta(days=365)
        elif period == "2y":
            start = end - timedelta(days=730)
        elif period == "5y":
            start = end - timedelta(days=1825)
        elif period == "10y":
            start = end - timedelta(days=3650)
        elif period == "ytd":
            start = datetime(end.year, 1, 1)
        else:  # max
            start = end - timedelta(days=3650)  # Default to 10 years
    
    # Determine time delta based on interval
    if interval == "1m":
        delta = timedelta(minutes=1)
    elif interval == "5m":
        delta = timedelta(minutes=5)
    elif interval == "15m":
        delta = timedelta(minutes=15)
    elif interval == "30m":
        delta = timedelta(minutes=30)
    elif interval == "1h":
        delta = timedelta(hours=1)
    elif interval == "1d":
        delta = timedelta(days=1)
    elif interval == "1wk":
        delta = timedelta(weeks=1)
    else:  # 1mo
        delta = timedelta(days=30)
    
    # Generate a deterministic but seemingly random base price based on symbol
    symbol_hash = sum(ord(c) for c in symbol)
    
    # Base price between $10 and $500
    base_price = 10 + (symbol_hash % 490)
    
    # Generate historical data points
    historical_data = []
    current_date = start
    current_price = base_price
    
    while current_date <= end:
        # Skip weekends for daily data or longer
        if interval in ["1d", "1wk", "1mo"] and current_date.weekday() >= 5:
            current_date += delta
            continue
        
        # Skip non-market hours for intraday data
        if interval in ["1m", "5m", "15m", "30m", "1h"] and (current_date.hour < 9 or current_date.hour >= 16 or (current_date.hour == 9 and current_date.minute < 30)):
            current_date += delta
            continue
        
        # Seed random with symbol and date for consistent results
        day_seed = symbol_hash + int(current_date.timestamp() / 86400)
        random.seed(day_seed)
        
        # Add some randomness to price (more volatile for shorter intervals)
        volatility = 0.02 if interval in ["1d", "1wk", "1mo"] else 0.005
        price_change = current_price * random.uniform(-volatility, volatility)
        current_price += price_change
        
        # Ensure price doesn't go below 1
        current_price = max(1, current_price)
        
        # Generate OHLC data
        if price_change > 0:
            day_open = current_price - random.uniform(0, abs(price_change))
            day_close = current_price
            day_high = current_price + random.uniform(0, current_price * 0.01)
            day_low = day_open - random.uniform(0, day_open * 0.01)
        else:
            day_open = current_price - price_change
            day_close = current_price
            day_high = day_open + random.uniform(0, day_open * 0.01)
            day_low = current_price - random.uniform(0, current_price * 0.01)
        
        # Ensure low <= open <= close <= high
        day_low = min(day_low, day_open, day_close)
        day_high = max(day_high, day_open, day_close)
        
        # Generate volume
        volume = random.randint(100000, 10000000)
        
        # Add data point
        historical_data.append({
            "date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
            "open": round(day_open, 2),
            "high": round(day_high, 2),
            "low": round(day_low, 2),
            "close": round(day_close, 2),
            "volume": volume
        })
        
        # Move to next interval
        current_date += delta
    
    # Generate company name based on symbol
    company_name = _get_company_name(symbol)
    
    return {
        "symbol": symbol,
        "company_name": company_name,
        "interval": interval,
        "currency": "USD",
        "historical_data": historical_data
    }

def _simulate_company_info(symbol: str) -> Dict[str, Any]:
    """
    Simulate company information.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary with simulated company information
    """
    # Generate a deterministic but seemingly random data based on symbol
    symbol_hash = sum(ord(c) for c in symbol)
    random.seed(symbol_hash)
    
    # Generate company name based on symbol
    company_name = _get_company_name(symbol)
    
    # Generate sector and industry
    sectors = [
        "Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
        "Communication Services", "Industrials", "Consumer Defensive", "Energy",
        "Basic Materials", "Real Estate", "Utilities"
    ]
    
    industries = {
        "Technology": ["Software", "Hardware", "Semiconductors", "IT Services", "Electronic Components"],
        "Healthcare": ["Biotechnology", "Pharmaceuticals", "Medical Devices", "Healthcare Services", "Health Insurance"],
        "Financial Services": ["Banks", "Insurance", "Asset Management", "Credit Services", "Capital Markets"],
        "Consumer Cyclical": ["Retail", "Automotive", "Entertainment", "Restaurants", "Travel & Leisure"],
        "Communication Services": ["Telecom", "Media", "Social Media", "Advertising", "Entertainment"],
        "Industrials": ["Aerospace & Defense", "Construction", "Manufacturing", "Transportation", "Business Services"],
        "Consumer Defensive": ["Food & Beverages", "Household Products", "Personal Products", "Tobacco", "Discount Stores"],
        "Energy": ["Oil & Gas", "Renewable Energy", "Coal", "Energy Services", "Pipelines"],
        "Basic Materials": ["Chemicals", "Metals & Mining", "Forest Products", "Building Materials", "Agriculture"],
        "Real Estate": ["REITs", "Real Estate Services", "Development", "Property Management", "Real Estate Holdings"],
        "Utilities": ["Electric Utilities", "Gas Utilities", "Water Utilities", "Renewable Utilities", "Multi-Utilities"]
    }
    
    sector = random.choice(sectors)
    industry = random.choice(industries[sector])
    
    # Generate other company data
    employees = random.randint(100, 200000)
    founded_year = random.randint(1950, 2020)
    
    # Generate address
    cities = ["New York", "San Francisco", "Chicago", "Seattle", "Boston", "Austin", "Los Angeles", "Denver"]
    states = ["NY", "CA", "IL", "WA", "MA", "TX", "CA", "CO"]
    city_idx = random.randint(0, len(cities) - 1)
    
    # Generate description
    descriptions = [
        f"{company_name} is a leading provider of {industry.lower()} solutions, serving customers worldwide.",
        f"{company_name} develops innovative products and services in the {industry.lower()} sector.",
        f"Founded in {founded_year}, {company_name} has grown to become a major player in the {sector.lower()} industry.",
        f"{company_name} specializes in {industry.lower()} technologies and services for businesses and consumers.",
        f"As a pioneer in {industry.lower()}, {company_name} continues to drive innovation and growth in the {sector.lower()} sector."
    ]
    
    return {
        "symbol": symbol,
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
        "description": random.choice(descriptions),
        "website": f"https://www.{symbol.lower()}.com",
        "employees": employees,
        "founded": founded_year,
        "headquarters": {
            "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Market', 'Tech', 'Park', 'Broadway'])} St",
            "city": cities[city_idx],
            "state": states[city_idx],
            "country": "United States",
            "zip": f"{random.randint(10000, 99999)}"
        },
        "executives": [
            {
                "name": f"{random.choice(['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller'])}",
                "title": "CEO",
                "year_born": random.randint(1950, 1980)
            },
            {
                "name": f"{random.choice(['Robert', 'Jennifer', 'William', 'Elizabeth', 'Richard', 'Susan'])} {random.choice(['Davis', 'Garcia', 'Rodriguez', 'Wilson', 'Martinez', 'Anderson'])}",
                "title": "CFO",
                "year_born": random.randint(1950, 1980)
            },
            {
                "name": f"{random.choice(['James', 'Mary', 'Thomas', 'Patricia', 'Charles', 'Linda'])} {random.choice(['Taylor', 'Thomas', 'Hernandez', 'Moore', 'Martin', 'Jackson'])}",
                "title": "CTO",
                "year_born": random.randint(1950, 1980)
            }
        ]
    }

def _simulate_stock_news(symbol: str) -> List[Dict[str, Any]]:
    """
    Simulate news articles related to a stock.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        List of simulated news articles
    """
    # Generate a deterministic but seemingly random seed based on symbol
    symbol_hash = sum(ord(c) for c in symbol)
    random.seed(symbol_hash + int(time.time() / 86400))  # Change seed daily
    
    # Generate company name based on symbol
    company_name = _get_company_name(symbol)
    
    # Generate news headlines
    headlines = [
        f"{company_name} Reports Strong Quarterly Earnings, Beats Expectations",
        f"{company_name} Announces New Product Line, Shares Rise",
        f"{company_name} Expands into New Markets, Analysts Optimistic",
        f"{company_name} CEO Discusses Future Growth Strategies in Interview",
        f"Analysts Upgrade {company_name} Stock, Cite Positive Outlook",
        f"{company_name} Partners with Tech Giant for New Initiative",
        f"{company_name} Faces Challenges in Competitive Market",
        f"Investors React to {company_name}'s Latest Announcement",
        f"{company_name} Addresses Industry Concerns at Annual Meeting",
        f"What's Next for {company_name}? Experts Weigh In"
    ]
    
    # Generate sources
    sources = ["Bloomberg", "Reuters", "CNBC", "Wall Street Journal", "Financial Times", "MarketWatch", "Barron's", "Investor's Business Daily"]
    
    # Generate news articles
    news = []
    num_articles = random.randint(3, 7)
    
    for i in range(num_articles):
        # Generate date within the last week
        days_ago = random.randint(0, 7)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Generate headline and summary
        headline = random.choice(headlines)
        headlines.remove(headline)  # Ensure no duplicate headlines
        
        summary = f"This is a simulated news summary for {company_name} ({symbol}). " + \
                 f"The article discusses recent developments and potential impact on the company's stock price. " + \
                 f"Investors and analysts are closely monitoring these developments."
        
        news.append({
            "headline": headline,
            "source": random.choice(sources),
            "date": date,
            "url": f"https://finance.example.com/news/{symbol.lower()}/{date.replace('-', '')}-{i}",
            "summary": summary
        })
    
    return news

def _simulate_stock_fundamentals(symbol: str) -> Dict[str, Any]:
    """
    Simulate fundamental financial data for a stock.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary with simulated fundamental data
    """
    # Generate a deterministic but seemingly random data based on symbol
    symbol_hash = sum(ord(c) for c in symbol)
    random.seed(symbol_hash)
    
    # Get quote data for reference
    quote = _simulate_stock_quote(symbol)
    price = quote["price"]
    market_cap = quote["market_cap"]
    
    # Generate revenue and earnings (last 4 quarters)
    base_quarterly_revenue = market_cap * random.uniform(0.05, 0.2) / 4
    base_quarterly_earnings = base_quarterly_revenue * random.uniform(0.05, 0.2)
    
    quarterly_data = []
    annual_data = []
    
    for i in range(4):
        quarter = 4 - i
        year = datetime.now().year
        if quarter <= 0:
            quarter += 4
            year -= 1
        
        # Add some randomness to quarterly data
        revenue = base_quarterly_revenue * (1 + random.uniform(-0.1, 0.1))
        earnings = base_quarterly_earnings * (1 + random.uniform(-0.15, 0.15))
        
        quarterly_data.append({
            "year": year,
            "quarter": quarter,
            "revenue": round(revenue, 2),
            "earnings": round(earnings, 2),
            "eps": round(earnings / (market_cap / price), 2)
        })
    
    # Generate annual data (last 3 years)
    for i in range(3):
        year = datetime.now().year - i
        
        # Aggregate quarterly data for annual
        if i == 0:
            # Current year (partial)
            revenue = sum(q["revenue"] for q in quarterly_data if q["year"] == year)
            earnings = sum(q["earnings"] for q in quarterly_data if q["year"] == year)
        else:
            # Previous years (full)
            revenue = base_quarterly_revenue * 4 * (1 - i * 0.05) * (1 + random.uniform(-0.1, 0.1))
            earnings = base_quarterly_earnings * 4 * (1 - i * 0.05) * (1 + random.uniform(-0.15, 0.15))
        
        annual_data.append({
            "year": year,
            "revenue": round(revenue, 2),
            "earnings": round(earnings, 2),
            "eps": round(earnings / (market_cap / price), 2)
        })
    
    # Generate other fundamental metrics
    return {
        "symbol": symbol,
        "quarterly_data": quarterly_data,
        "annual_data": annual_data,
        "metrics": {
            "pe_ratio": quote["pe_ratio"],
            "forward_pe": round(quote["pe_ratio"] * random.uniform(0.8, 1.1), 2),
            "peg_ratio": round(random.uniform(0.5, 2.5), 2),
            "price_to_sales": round(market_cap / (base_quarterly_revenue * 4), 2),
            "price_to_book": round(random.uniform(1, 10), 2),
            "debt_to_equity": round(random.uniform(0, 2), 2),
            "roe": round(random.uniform(0.05, 0.3), 4),
            "roa": round(random.uniform(0.02, 0.15), 4),
            "profit_margin": round(random.uniform(0.05, 0.3), 4),
            "operating_margin": round(random.uniform(0.1, 0.4), 4),
            "beta": round(random.uniform(0.5, 2), 2),
            "dividend_yield": quote["dividend_yield"],
            "dividend_payout_ratio": round(random.uniform(0, 0.7), 2)
        }
    }

def _get_company_name(symbol: str) -> str:
    """
    Generate a company name based on the stock symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Generated company name
    """
    # Common company name suffixes
    suffixes = ["Inc.", "Corporation", "Corp.", "Technologies", "Enterprises", "Group", "Holdings", "Systems", "Solutions"]
    
    # Check for known symbols
    known_companies = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc.",
        "AMZN": "Amazon.com, Inc.",
        "META": "Meta Platforms, Inc.",
        "TSLA": "Tesla, Inc.",
        "NVDA": "NVIDIA Corporation",
        "JPM": "JPMorgan Chase & Co.",
        "V": "Visa Inc.",
        "WMT": "Walmart Inc.",
        "JNJ": "Johnson & Johnson",
        "PG": "Procter & Gamble Company",
        "MA": "Mastercard Incorporated",
        "UNH": "UnitedHealth Group Incorporated",
        "HD": "The Home Depot, Inc.",
        "BAC": "Bank of America Corporation",
        "XOM": "Exxon Mobil Corporation",
        "PFE": "Pfizer Inc.",
        "CSCO": "Cisco Systems, Inc.",
        "ADBE": "Adobe Inc."
    }
    
    if symbol in known_companies:
        return known_companies[symbol]
    
    # Generate a name based on the symbol
    if len(symbol) <= 2:
        # For very short symbols, expand them
        return f"{symbol} {random.choice(suffixes)}"
    
    # Try to make a readable name from the symbol
    vowels = "aeiou"
    name_parts = []
    
    # Split the symbol into parts
    i = 0
    while i < len(symbol):
        if i + 2 <= len(symbol):
            name_parts.append(symbol[i:i+2])
            i += 2
        else:
            name_parts.append(symbol[i])
            i += 1
    
    # Make each part more readable by adding vowels if needed
    readable_parts = []
    for part in name_parts:
        if any(v in part.lower() for v in vowels):
            readable_parts.append(part.capitalize())
        else:
            readable_parts.append(part.capitalize() + random.choice(vowels))
    
    # Combine parts and add suffix
    company_name = "".join(readable_parts) + " " + random.choice(suffixes)
    
    return company_name
