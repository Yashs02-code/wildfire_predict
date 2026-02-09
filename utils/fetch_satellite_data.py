import requests
import datetime
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configurations
NASA_MAP_KEY = os.getenv("NASA_FIRMS_MAP_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def fetch_firms_data(region, from_date, to_date):
    """
    Fetches real-time hotspot data from NASA FIRMS API.
    """
    if not NASA_MAP_KEY or NASA_MAP_KEY == "YOUR_NASA_MAP_KEY_HERE":
        logger.warning("NASA Map Key missing. Using simulated data.")
        return simulate_firms_data(from_date)

    # NASA FIRMS API for India (IND)
    # Using VIIRS_SNPP_NRT as a reliable source
    url = f"https://firms.modaps.eosdis.nasa.gov/api/country/json/{NASA_MAP_KEY}/VIIRS_SNPP_NRT/IND/1"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Filter by region name if it's in the response, otherwise return all India points
            # FIRMS doesn't always provide 'state' in country-level JSON, so we return all India points
            # for the regional context in the dashboard.
            logger.info(f"Fetched {len(data)} live hotspots from NASA FIRMS.")
            return data
        else:
            logger.error(f"NASA FIRMS API Error: {response.status_code}")
            return simulate_firms_data(from_date)
    except Exception as e:
        logger.error(f"Failed to fetch NASA data: {e}")
        return simulate_firms_data(from_date)

def fetch_weather_data(region):
    """
    Fetches real-time weather data for a region using OpenWeatherMap.
    """
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY_HERE":
        logger.warning("Weather API Key missing. Using simulated weather.")
        return simulate_weather_data()

    # Append country to region for better accuracy
    city_query = f"{region},IN"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_query}&appid={WEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            wdat = response.json()
            return {
                'temperature': wdat['main']['temp'],
                'humidity': wdat['main']['humidity'],
                'wind_speed': wdat['wind']['speed'] * 3.6, # convert m/s to km/h
                'rainfall': wdat.get('rain', {}).get('1h', 0),
                'ndvi': round(0.5 + (wdat['main']['temp'] / 100), 2) # Heuristic for now
            }
        else:
            logger.error(f"Weather API Error: {response.status_code}")
            return simulate_weather_data()
    except Exception as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return simulate_weather_data()

# --- Fallback Simulation Functions ---

def simulate_firms_data(date):
    import random
    num_points = random.randint(5, 50)
    data = []
    for _ in range(num_points):
        data.append({
            'latitude': random.uniform(15, 25), # Typical India latitude
            'longitude': random.uniform(70, 85),
            'brightness': random.uniform(300, 500),
            'acq_date': date,
            'confidence': random.randint(40, 100)
        })
    return data

def simulate_weather_data():
    import random
    return {
        'temperature': round(random.uniform(20, 45), 2),
        'humidity': round(random.uniform(10, 60), 2),
        'wind_speed': round(random.uniform(5, 35), 2),
        'rainfall': round(random.uniform(0, 10), 2),
        'ndvi': round(random.uniform(0.1, 0.8), 2)
    }
