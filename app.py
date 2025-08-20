import os 
import requests 
import openmeteo_requests 
import pandas as pd 
import requests_cache 
from retry_requests import retry 
from dotenv import load_dotenv 
from portia import ( 
    Config, 
    LLMProvider, 
    Portia, 
    Tool,  # Import Tool class instead of tool decorator
    ToolRunContext
) 
from pydantic import BaseModel
from typing import Any

# Load environment variables 
load_dotenv() 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
 
# Setup Open-Meteo client with caching and retries 
cache_session = requests_cache.CachedSession(".cache", expire_after=3600) 
retry_session = retry(cache_session, retries=5, backoff_factor=0.2) 
openmeteo = openmeteo_requests.Client(session=retry_session) 
 
# Free geocoding using Open-Meteo's endpoint 
def geocode_city(city: str): 
    """Convert city name to latitude & longitude using Open-Meteo geocoding API.""" 
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1" 
    resp = requests.get(url).json() 
    if "results" not in resp or len(resp["results"]) == 0: 
        raise ValueError(f"City '{city}' not found.") 
    loc = resp["results"][0] 
    return loc["latitude"], loc["longitude"]

# Define the input schema for the tool
class WeatherToolArgs(BaseModel):
    city: str
    hours: int = 6

# Create the Weather Tool class
class WeatherTool(Tool[dict]):
    id: str = "weather_tool"
    name: str = "Weather Forecast Tool"
    description: str = "Get hourly weather forecast (temperature in °C) for a city"
    args_schema: type[BaseModel] = WeatherToolArgs
    output_schema: tuple[str, str] = ("dict", "Weather data with timestamps and temperature readings")
    should_summarize: bool = True
    
    def run(self, ctx: ToolRunContext, *args: Any, **kwargs: Any) -> dict:
        """
        Get hourly weather forecast (temperature in °C) for a city.
        """
        # Extract arguments
        city = kwargs.get('city')
        hours = kwargs.get('hours', 6)
        
        lat, lon = geocode_city(city)
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
        }
        
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        # Extract hourly data
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        
        hourly_data = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
        
        df = pd.DataFrame({
            "date": hourly_data,
            "temperature_2m": hourly_temperature_2m
        }).head(hours)
        
        return df.to_dict(orient="records")

# Create an instance of the tool
weather_tool = WeatherTool()

# ---- Configure Portia ---- 
google_config = Config.from_default( 
    llm_provider=LLMProvider.GOOGLE, 
    default_model="google/gemini-2.0-flash", 
    google_api_key=GOOGLE_API_KEY 
) 
 
# Create Portia with the tool instance
portia = Portia(config=google_config, tools=[weather_tool])
 
# ---- Example Run ---- 
plan_run = portia.run( 
    "Which is a better destination to visit now, Kerala or Shimla? Check weather reports and tell me." 
) 
print(plan_run.model_dump_json(indent=2))