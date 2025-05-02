"""
Weather Checker Tool for the Personal AI Agent System.

This module provides functionality to retrieve current weather conditions,
forecasts, and historical weather data for specified locations.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logger = logging.getLogger("weather_checker")

def run(
    location: str,
    query_type: str = "current",
    units: str = "metric",
    days: int = 5,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_hourly: bool = False,
    include_alerts: bool = True,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["weather", "location"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Retrieve weather information for a specified location.
    
    Args:
        location: Location name or coordinates (e.g., "New York", "40.7128,-74.0060")
        query_type: Type of weather data to retrieve (current, forecast, historical)
        units: Unit system (metric, imperial)
        days: Number of days for forecast (1-10)
        start_date: Start date for historical data (YYYY-MM-DD)
        end_date: End date for historical data (YYYY-MM-DD)
        include_hourly: Whether to include hourly forecast data
        include_alerts: Whether to include weather alerts
        store_memory: Whether to store the weather data in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing weather information
    """
    logger.info(f"Retrieving {query_type} weather data for {location}")
    
    try:
        # Validate inputs
        if not location:
            raise ValueError("Location is required")
            
        if query_type not in ["current", "forecast", "historical"]:
            raise ValueError(f"Invalid query type: {query_type}. Supported types: current, forecast, historical")
            
        if units not in ["metric", "imperial"]:
            raise ValueError(f"Invalid units: {units}. Supported units: metric, imperial")
            
        if days < 1 or days > 10:
            raise ValueError(f"Days must be between 1 and 10, got {days}")
            
        if query_type == "historical" and (not start_date or not end_date):
            raise ValueError("Start date and end date are required for historical data")
        
        # In a real implementation, this would use a weather API
        # For now, we'll simulate the weather data
        
        # Simulate weather data retrieval
        if query_type == "current":
            weather_data = _simulate_current_weather(location, units)
        elif query_type == "forecast":
            weather_data = _simulate_forecast_weather(location, units, days, include_hourly, include_alerts)
        else:  # historical
            weather_data = _simulate_historical_weather(location, units, start_date, end_date)
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a summary of the weather data for memory storage
                if query_type == "current":
                    summary = f"Current weather in {location}: {weather_data['current']['condition']['text']}, {weather_data['current']['temp_c']}°C ({weather_data['current']['temp_f']}°F)"
                elif query_type == "forecast":
                    summary = f"Weather forecast for {location}: Today - {weather_data['forecast']['forecastday'][0]['day']['condition']['text']}, {weather_data['forecast']['forecastday'][0]['day']['avgtemp_c']}°C"
                else:  # historical
                    summary = f"Historical weather for {location} from {start_date} to {end_date}"
                
                memory_entry = {
                    "type": "weather_data",
                    "location": location,
                    "query_type": query_type,
                    "summary": summary,
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + [location.lower().replace(" ", "_")]
                )
                
                logger.info(f"Stored weather data in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store weather data in memory: {str(e)}")
        
        return {
            "success": True,
            "location": location,
            "query_type": query_type,
            "units": units,
            "data": weather_data
        }
    except Exception as e:
        error_msg = f"Error retrieving weather data: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "location": location,
            "query_type": query_type
        }

def _simulate_current_weather(location: str, units: str) -> Dict[str, Any]:
    """
    Simulate current weather data for a location.
    
    Args:
        location: Location name or coordinates
        units: Unit system (metric, imperial)
        
    Returns:
        Dictionary with simulated current weather data
    """
    # Generate a deterministic but seemingly random temperature based on location
    location_hash = sum(ord(c) for c in location)
    random.seed(location_hash + int(time.time() / 86400))  # Change seed daily
    
    # Generate temperature based on location and current date
    base_temp_c = random.uniform(15, 25)  # Base temperature in Celsius
    
    # Adjust for northern/southern hemisphere and season
    current_month = datetime.now().month
    if "australia" in location.lower() or "argentina" in location.lower() or "south africa" in location.lower():
        # Southern hemisphere
        seasonal_adjustment = 10 * math.cos((current_month - 1) * math.pi / 6)
    else:
        # Northern hemisphere
        seasonal_adjustment = 10 * math.cos((current_month - 7) * math.pi / 6)
    
    temp_c = round(base_temp_c + seasonal_adjustment, 1)
    temp_f = round((temp_c * 9/5) + 32, 1)
    
    # Generate other weather parameters
    humidity = random.randint(30, 90)
    wind_kph = random.uniform(5, 30)
    wind_mph = round(wind_kph * 0.621371, 1)
    pressure_mb = random.uniform(980, 1030)
    pressure_in = round(pressure_mb * 0.02953, 2)
    
    # Determine condition based on temperature and randomness
    if temp_c > 30:
        conditions = ["Sunny", "Clear", "Hot"]
        condition = random.choice(conditions)
        icon = "113.png"  # Sunny icon
    elif temp_c > 20:
        conditions = ["Partly cloudy", "Mostly sunny", "Clear"]
        condition = random.choice(conditions)
        icon = "116.png"  # Partly cloudy icon
    elif temp_c > 10:
        conditions = ["Cloudy", "Overcast", "Partly cloudy"]
        condition = random.choice(conditions)
        icon = "119.png"  # Cloudy icon
    elif temp_c > 0:
        conditions = ["Cloudy", "Overcast", "Light rain", "Drizzle"]
        condition = random.choice(conditions)
        icon = "266.png"  # Light rain icon
    else:
        conditions = ["Snow", "Light snow", "Freezing", "Overcast"]
        condition = random.choice(conditions)
        icon = "338.png"  # Snow icon
    
    # Generate current time in location (simplified)
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return {
        "location": {
            "name": location.split(",")[0],
            "region": "",
            "country": "",
            "lat": 0.0,
            "lon": 0.0,
            "tz_id": "UTC",
            "localtime": local_time
        },
        "current": {
            "last_updated": local_time,
            "temp_c": temp_c,
            "temp_f": temp_f,
            "is_day": 1 if 6 <= datetime.now().hour <= 18 else 0,
            "condition": {
                "text": condition,
                "icon": f"//cdn.weatherapi.com/weather/64x64/day/{icon}",
                "code": random.randint(1000, 1030)
            },
            "wind_mph": wind_mph,
            "wind_kph": wind_kph,
            "wind_degree": random.randint(0, 359),
            "wind_dir": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "pressure_mb": pressure_mb,
            "pressure_in": pressure_in,
            "precip_mm": random.uniform(0, 5) if "rain" in condition.lower() else 0,
            "precip_in": random.uniform(0, 0.2) if "rain" in condition.lower() else 0,
            "humidity": humidity,
            "cloud": random.randint(0, 100),
            "feelslike_c": temp_c - random.uniform(0, 3) if temp_c > 25 else temp_c + random.uniform(0, 3),
            "feelslike_f": temp_f - random.uniform(0, 5) if temp_f > 77 else temp_f + random.uniform(0, 5),
            "vis_km": random.uniform(5, 20),
            "vis_miles": random.uniform(3, 12),
            "uv": random.uniform(1, 10),
            "gust_mph": wind_mph + random.uniform(2, 10),
            "gust_kph": wind_kph + random.uniform(3, 15)
        }
    }

def _simulate_forecast_weather(
    location: str,
    units: str,
    days: int,
    include_hourly: bool,
    include_alerts: bool
) -> Dict[str, Any]:
    """
    Simulate forecast weather data for a location.
    
    Args:
        location: Location name or coordinates
        units: Unit system (metric, imperial)
        days: Number of days for forecast
        include_hourly: Whether to include hourly forecast
        include_alerts: Whether to include weather alerts
        
    Returns:
        Dictionary with simulated forecast weather data
    """
    # Get current weather as a starting point
    current_weather = _simulate_current_weather(location, units)
    
    # Generate forecast for the specified number of days
    forecast_days = []
    
    # Get the starting temperature from current weather
    base_temp_c = current_weather["current"]["temp_c"]
    
    for day in range(days):
        # Calculate date
        date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        
        # Vary temperature slightly for each day
        day_temp_c = base_temp_c + random.uniform(-5, 5)
        max_temp_c = day_temp_c + random.uniform(2, 8)
        min_temp_c = day_temp_c - random.uniform(2, 8)
        
        # Convert to Fahrenheit
        max_temp_f = (max_temp_c * 9/5) + 32
        min_temp_f = (min_temp_c * 9/5) + 32
        avg_temp_c = (max_temp_c + min_temp_c) / 2
        avg_temp_f = (max_temp_f + min_temp_f) / 2
        
        # Determine condition based on temperature
        if avg_temp_c > 30:
            condition = random.choice(["Sunny", "Clear", "Hot"])
            icon = "113.png"
        elif avg_temp_c > 20:
            condition = random.choice(["Partly cloudy", "Mostly sunny", "Clear"])
            icon = "116.png"
        elif avg_temp_c > 10:
            condition = random.choice(["Cloudy", "Overcast", "Partly cloudy"])
            icon = "119.png"
        elif avg_temp_c > 0:
            condition = random.choice(["Cloudy", "Overcast", "Light rain", "Drizzle"])
            icon = "266.png"
        else:
            condition = random.choice(["Snow", "Light snow", "Freezing", "Overcast"])
            icon = "338.png"
        
        # Generate other weather parameters
        humidity = random.randint(30, 90)
        wind_kph = random.uniform(5, 30)
        wind_mph = round(wind_kph * 0.621371, 1)
        
        # Generate hourly forecast if requested
        hourly = []
        if include_hourly:
            for hour in range(24):
                # Calculate time
                time = f"{date} {hour:02d}:00"
                
                # Vary temperature throughout the day
                hour_factor = math.sin(hour * math.pi / 12 - math.pi/2) * 0.5 + 0.5  # 0 to 1 factor, peaks at hour 12
                hour_temp_c = min_temp_c + (max_temp_c - min_temp_c) * hour_factor
                hour_temp_f = (hour_temp_c * 9/5) + 32
                
                # Determine condition based on time and base condition
                if 6 <= hour <= 18:  # Daytime
                    hour_condition = condition
                else:  # Nighttime
                    if "rain" in condition.lower() or "snow" in condition.lower():
                        hour_condition = condition
                    else:
                        hour_condition = condition.replace("Sunny", "Clear").replace("Mostly sunny", "Clear")
                
                hourly.append({
                    "time": time,
                    "temp_c": round(hour_temp_c, 1),
                    "temp_f": round(hour_temp_f, 1),
                    "condition": {
                        "text": hour_condition,
                        "icon": f"//cdn.weatherapi.com/weather/64x64/{'day' if 6 <= hour <= 18 else 'night'}/{icon}",
                        "code": random.randint(1000, 1030)
                    },
                    "wind_mph": wind_mph + random.uniform(-5, 5),
                    "wind_kph": wind_kph + random.uniform(-8, 8),
                    "wind_degree": random.randint(0, 359),
                    "wind_dir": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                    "humidity": humidity + random.randint(-10, 10),
                    "cloud": random.randint(0, 100),
                    "feelslike_c": hour_temp_c - random.uniform(0, 3) if hour_temp_c > 25 else hour_temp_c + random.uniform(0, 3),
                    "feelslike_f": hour_temp_f - random.uniform(0, 5) if hour_temp_f > 77 else hour_temp_f + random.uniform(0, 5),
                    "chance_of_rain": random.randint(0, 100) if "rain" in condition.lower() else random.randint(0, 20),
                    "chance_of_snow": random.randint(0, 100) if "snow" in condition.lower() else random.randint(0, 10)
                })
        
        # Add day to forecast
        forecast_days.append({
            "date": date,
            "day": {
                "maxtemp_c": round(max_temp_c, 1),
                "maxtemp_f": round(max_temp_f, 1),
                "mintemp_c": round(min_temp_c, 1),
                "mintemp_f": round(min_temp_f, 1),
                "avgtemp_c": round(avg_temp_c, 1),
                "avgtemp_f": round(avg_temp_f, 1),
                "condition": {
                    "text": condition,
                    "icon": f"//cdn.weatherapi.com/weather/64x64/day/{icon}",
                    "code": random.randint(1000, 1030)
                },
                "uv": random.uniform(1, 10),
                "humidity": humidity,
                "chance_of_rain": random.randint(0, 100) if "rain" in condition.lower() else random.randint(0, 20),
                "chance_of_snow": random.randint(0, 100) if "snow" in condition.lower() else random.randint(0, 10)
            },
            "astro": {
                "sunrise": f"{random.randint(5, 7)}:{random.randint(0, 59):02d} AM",
                "sunset": f"{random.randint(5, 7)}:{random.randint(0, 59):02d} PM",
                "moonrise": f"{random.randint(7, 11)}:{random.randint(0, 59):02d} PM",
                "moonset": f"{random.randint(5, 9)}:{random.randint(0, 59):02d} AM",
                "moon_phase": random.choice(["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]),
                "moon_illumination": f"{random.randint(0, 100)}"
            }
        })
        
        # Add hourly forecast if requested
        if include_hourly:
            forecast_days[-1]["hour"] = hourly
    
    # Generate alerts if requested
    alerts = []
    if include_alerts and random.random() < 0.2:  # 20% chance of having an alert
        alert_types = ["Flood Warning", "Severe Thunderstorm Warning", "Heat Advisory", "Wind Advisory", "Winter Storm Warning"]
        alerts = [{
            "headline": random.choice(alert_types),
            "severity": random.choice(["Moderate", "Severe", "Extreme"]),
            "urgency": random.choice(["Expected", "Immediate"]),
            "areas": location.split(",")[0],
            "category": "Met",
            "certainty": random.choice(["Possible", "Likely", "Observed"]),
            "event": random.choice(alert_types),
            "note": "This is a simulated weather alert for demonstration purposes.",
            "effective": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "expires": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "desc": f"The National Weather Service has issued a {random.choice(alert_types)} for {location.split(',')[0]} and surrounding areas.",
            "instruction": "Take appropriate precautions."
        }]
    
    # Combine everything into the forecast response
    forecast = {
        "location": current_weather["location"],
        "current": current_weather["current"],
        "forecast": {
            "forecastday": forecast_days
        }
    }
    
    # Add alerts if available
    if include_alerts and alerts:
        forecast["alerts"] = {
            "alert": alerts
        }
    
    return forecast

def _simulate_historical_weather(
    location: str,
    units: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Simulate historical weather data for a location.
    
    Args:
        location: Location name or coordinates
        units: Unit system (metric, imperial)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Dictionary with simulated historical weather data
    """
    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Calculate number of days
    days = (end - start).days + 1
    
    if days < 1:
        raise ValueError("End date must be after start date")
    
    if days > 30:
        raise ValueError("Historical data is limited to 30 days")
    
    # Generate a deterministic but seemingly random temperature based on location
    location_hash = sum(ord(c) for c in location)
    
    # Generate historical data for each day
    historical_days = []
    
    for day in range(days):
        # Calculate date
        date = (start + timedelta(days=day)).strftime("%Y-%m-%d")
        
        # Seed random with location and date for consistent results
        day_seed = location_hash + int(datetime.strptime(date, "%Y-%m-%d").timestamp() / 86400)
        random.seed(day_seed)
        
        # Generate temperature based on location and date
        month = datetime.strptime(date, "%Y-%m-%d").month
        base_temp_c = random.uniform(15, 25)  # Base temperature in Celsius
        
        # Adjust for northern/southern hemisphere and season
        if "australia" in location.lower() or "argentina" in location.lower() or "south africa" in location.lower():
            # Southern hemisphere
            seasonal_adjustment = 10 * math.cos((month - 1) * math.pi / 6)
        else:
            # Northern hemisphere
            seasonal_adjustment = 10 * math.cos((month - 7) * math.pi / 6)
        
        day_temp_c = base_temp_c + seasonal_adjustment
        max_temp_c = day_temp_c + random.uniform(2, 8)
        min_temp_c = day_temp_c - random.uniform(2, 8)
        
        # Convert to Fahrenheit
        max_temp_f = (max_temp_c * 9/5) + 32
        min_temp_f = (min_temp_c * 9/5) + 32
        avg_temp_c = (max_temp_c + min_temp_c) / 2
        avg_temp_f = (max_temp_f + min_temp_f) / 2
        
        # Determine condition based on temperature
        if avg_temp_c > 30:
            condition = random.choice(["Sunny", "Clear", "Hot"])
            icon = "113.png"
        elif avg_temp_c > 20:
            condition = random.choice(["Partly cloudy", "Mostly sunny", "Clear"])
            icon = "116.png"
        elif avg_temp_c > 10:
            condition = random.choice(["Cloudy", "Overcast", "Partly cloudy"])
            icon = "119.png"
        elif avg_temp_c > 0:
            condition = random.choice(["Cloudy", "Overcast", "Light rain", "Drizzle"])
            icon = "266.png"
        else:
            condition = random.choice(["Snow", "Light snow", "Freezing", "Overcast"])
            icon = "338.png"
        
        # Generate other weather parameters
        humidity = random.randint(30, 90)
        wind_kph = random.uniform(5, 30)
        wind_mph = round(wind_kph * 0.621371, 1)
        
        # Add day to historical data
        historical_days.append({
            "date": date,
            "day": {
                "maxtemp_c": round(max_temp_c, 1),
                "maxtemp_f": round(max_temp_f, 1),
                "mintemp_c": round(min_temp_c, 1),
                "mintemp_f": round(min_temp_f, 1),
                "avgtemp_c": round(avg_temp_c, 1),
                "avgtemp_f": round(avg_temp_f, 1),
                "condition": {
                    "text": condition,
                    "icon": f"//cdn.weatherapi.com/weather/64x64/day/{icon}",
                    "code": random.randint(1000, 1030)
                },
                "uv": random.uniform(1, 10),
                "humidity": humidity,
                "precip_mm": random.uniform(0, 10) if "rain" in condition.lower() else random.uniform(0, 1),
                "precip_in": random.uniform(0, 0.4) if "rain" in condition.lower() else random.uniform(0, 0.04)
            }
        })
    
    # Combine everything into the historical response
    return {
        "location": {
            "name": location.split(",")[0],
            "region": "",
            "country": "",
            "lat": 0.0,
            "lon": 0.0,
            "tz_id": "UTC"
        },
        "historical": {
            "forecastday": historical_days
        }
    }

# Import math for calculations
import math
