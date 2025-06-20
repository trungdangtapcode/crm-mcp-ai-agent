"""
Weather information tools for MCP server
"""
from datetime import datetime
from typing import Dict, List, Any
from config import WEATHER_API_KEY
import os
import requests

def func_weather_info(location: str) -> Dict[str, Any]:
    """
    Get current weather information for a location
    
    Args:
        location: City name, zip code, or coordinates
    
    Returns:
        Weather information including temperature and conditions
    """

    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': WEATHER_API_KEY,
        'q': location
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'error' in data:
            raise Exception(f"Weather API Error: {data['error']['message']}")
        current = data['current']
        location_data = data['location']
        weather_data = {
            "location": location_data['name'],
            "temperature": current['temp_c'],
            "temperature_unit": "celsius",
            "conditions": current['condition']['text'],
            "humidity": current['humidity'],
            "wind_speed": current['wind_kph'],
            "wind_direction": current['wind_dir'],
            "timestamp": current['last_updated']
        }
        return weather_data
    else:
        raise Exception(f"Failed to fetch weather data: {response.status_code}")

def func_forecast(location: str, days: int = 5) -> List[Dict[str, Any]]:
    """
    Get weather forecast for a location
    
    Args:
        location: City name, zip code, or coordinates
        days: Number of days to forecast (default: 5, max: 14)
    
    Returns:
        List of daily weather forecasts
    """
    if days < 1 or days > 14:
        raise ValueError("days must be between 1 and 14")
    
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': WEATHER_API_KEY,
        'q': location,
        'days': days
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'error' in data:
            raise Exception(f"Weather API Error: {data['error']['message']}")
        forecast_list = []
        for day in data['forecast']['forecastday']:
            day_data = day['day']
            date_str = day['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_of_week = date_obj.strftime('%A')
            forecast_data = {
                "location": data['location']['name'],
                "date": date_str,
                "day": day_of_week,
                "condition": day_data['condition']['text'],
                "temperature_high": day_data['maxtemp_c'],
                "temperature_low": day_data['mintemp_c'],
                "temperature_unit": "celsius",
                "precipitation_chance": day_data['daily_chance_of_rain']
            }
            forecast_list.append(forecast_data)
        return forecast_list
    else:
        raise Exception(f"Failed to fetch forecast data: {response.status_code}")

def register_weather_tools(mcp):
    """Register weather-related tools with the MCP server"""
    
    @mcp.tool
    def weather_info(location: str) -> Dict[str, Any]:
        """
        Get current weather information for a location
        
        Args:
            location: City name, zip code, or coordinates
        
        Returns:
            Weather information including temperature and conditions
        """
        return func_weather_info(location)
    
    @mcp.tool
    def forecast(location: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        Get weather forecast for a location
        
        Args:
            location: City name, zip code, or coordinates
            days: Number of days to forecast (default: 5, max: 14)
        
        Returns:
            List of daily weather forecasts
        """
        return func_forecast(location, days)


if __name__ == "__main__":
    location = "San Francisco"
    weather = func_forecast(location)
    print(weather)