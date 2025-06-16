"""
Weather information tools for MCP server
"""
from datetime import datetime
from typing import Dict, List, Any

def register_weather_tools(mcp):
    """Register weather-related tools with the MCP server"""
    
    @mcp.tool
    def weather_info(location: str) -> Dict[str, Any]:
        """
        Get current weather information for a location
        
        Args:
            location: City name or location to get weather for
        
        Returns:
            Weather information including temperature and conditions
        """
        # In a real application, you would call a weather API here
        # This is a mock response
        mock_weather = {
            "location": location,
            "temperature": 22,
            "temperature_unit": "celsius",
            "conditions": "partly cloudy",
            "humidity": 65,
            "wind_speed": 10,
            "wind_direction": "NE",
            "timestamp": datetime.now().isoformat()
        }
        return mock_weather
    
    @mcp.tool
    def forecast(location: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        Get weather forecast for a location
        
        Args:
            location: City name or location to get forecast for
            days: Number of days to forecast (default: 5)
        
        Returns:
            List of daily weather forecasts
        """
        import random
        
        # Mock weather conditions
        conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "thunderstorms", "snowy"]
        
        # Generate mock forecast
        forecast_data = []
        for i in range(days):
            # Generate random but somewhat realistic data
            temp_high = round(20 + random.uniform(-5, 10), 1)
            temp_low = round(temp_high - random.uniform(5, 10), 1)
            condition = random.choice(conditions)
            
            # Add a day to current date
            day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            day = day.replace(day=day.day + i)
            
            forecast_data.append({
                "location": location,
                "date": day.strftime("%Y-%m-%d"),
                "day": day.strftime("%A"),
                "condition": condition,
                "temperature_high": temp_high,
                "temperature_low": temp_low,
                "temperature_unit": "celsius",
                "precipitation_chance": round(random.uniform(0, 100), 0)
            })
            
        return forecast_data
