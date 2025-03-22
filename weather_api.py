import requests
import json
import logging

# API keys and endpoints
OPENCAGE_API_KEY = "b5b5222d8fbf4508972c0dd9073ebf92"
OPENCAGE_API_URL = "https://api.opencagedata.com/geocode/v1/json"
API_URL = "https://api.open-meteo.com/v1/forecast"
NEWS_API_URL = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "cad23b4570454e438655bfe186f10620"  # Replace with your NewsAPI key

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_location_data(city):
    """Fetches latitude and longitude for a given city using the OpenCage Geocode API."""
    logging.info(f"Fetching location data for city: {city}")
    geocode_params = {
        "q": city,
        "key": OPENCAGE_API_KEY
    }
    
    try:
        response = requests.get(OPENCAGE_API_URL, params=geocode_params)
        response.raise_for_status()  # Raise exception for bad HTTP responses
        
        data = response.json()
        
        if data['results']:
            location = data['results'][0]['geometry']
            latitude = location['lat']
            longitude = location['lng']
            logging.info(f"Location found: Latitude {latitude}, Longitude {longitude}")
            return latitude, longitude
        else:
            logging.warning(f"City not found: {city}")
            return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching location data for {city}: {e}")
        return None

def get_weather_data(latitude, longitude):
    """Fetches the current weather for the given latitude and longitude."""
    logging.info(f"Fetching weather data for latitude: {latitude}, longitude: {longitude}")
    
    current_weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "timezone": "auto"
    }

    try:
        current_weather_response = requests.get(API_URL, params=current_weather_params)
        current_weather_response.raise_for_status()
        
        current_weather_data = current_weather_response.json()
        
        if 'current_weather' in current_weather_data:
            current_weather = current_weather_data['current_weather']
            temperature = current_weather.get('temperature', 'N/A')
            wind_speed = current_weather.get('windspeed', 'N/A')
            humidity = current_weather.get('humidity', 'N/A')
            precip = current_weather.get('precipitation', 0)

            # Determine weather icon based on conditions
            icon = get_weather_icon(temperature, wind_speed, precip)

            return {
                'temperature': temperature,
                'windspeed': wind_speed,
                'humidity': humidity,
                'precipitation': precip,
                'icon': icon
            }
        else:
            logging.warning(f"Error: No current weather data found for {latitude}, {longitude}")
            return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return None

def get_weather_icon(temperature, wind_speed, precip):
    """Determines the appropriate weather icon."""
    # Convert wind speed to mph and precipitation to inches
    wind_speed_mph = wind_speed * 0.621371
    precip_in = precip * 0.0393701  # Convert mm to inches
    
    if precip_in > 0.2:  # Rain threshold (over 0.2 inches)
        return "rain_icon.png"
    elif wind_speed_mph > 15:  # Wind threshold (over 15 mph)
        return "wind_icon.png"
    elif temperature < 17:  # Temperature threshold (below 62.6°F)
        return "cloudy_icon.png"
    else:
        return "sun_icon.png"

def get_forecast_data(latitude, longitude):
    """Fetch weather forecast from Open Meteo API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,windspeed_10m_max,precipitation_sum&timezone=auto"
    
    # Send the GET request to the API
    response = requests.get(url)

    # Check if the response is successful (status code 200)
    if response.status_code == 200:
        try:
            # Attempt to parse the response as JSON
            forecast_data = response.json()
            logging.debug(f"Forecast data: {forecast_data}")  # Log the structure of the response
            return forecast_data
        except ValueError:
            logging.error("Failed to parse JSON response from the forecast API.")
            return None
    else:
        logging.error(f"Error fetching forecast data: {response.status_code}")
        return None

def save_weather_data(city, data):
    """Saves the weather data to a JSON file."""
    logging.info(f"Saving weather data for {city}...")
    try:
        # Load existing weather data
        with open("weather_data.json", "r+") as f:
            existing_data = json.load(f)
            existing_data[city] = data
            f.seek(0)
            json.dump(existing_data, f, indent=4)
        logging.info(f"Weather data for {city} saved successfully.")
        
    except Exception as e:
        logging.error(f"Error saving weather data for {city}: {e}")

def load_weather_data():
    """Loads previously saved weather data from the JSON file."""
    try:
        with open("weather_data.json", "r") as f:
            saved_data = json.load(f)
        logging.info("Weather data loaded successfully.")
        return saved_data
    except FileNotFoundError:
        logging.warning("Weather data file not found. Returning empty data.")
        return {}
    except Exception as e:
        logging.error(f"Error loading weather data: {e}")
        return {}

def get_weather_news():
    """Fetches weather-related news using the NewsAPI."""
    logging.info("Fetching weather news...")
    news_params = {
        "q": "weather",
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "relevancy"
    }
    
    try:
        news_response = requests.get(NEWS_API_URL, params=news_params)
        news_response.raise_for_status()
        
        if news_response.status_code == 200:
            news_data = news_response.json()
            articles = news_data.get("articles", [])
            logging.info("Weather news fetched successfully.")
            return articles
        else:
            logging.warning("Failed to fetch news data.")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather news: {e}")
        return None

def format_forecast_data(forecast_data):
    """Format the forecast data into a user-friendly string."""
    forecast_info = ""
    if forecast_data and 'daily' in forecast_data:
        daily_data = forecast_data['daily']
        for idx, date in enumerate(daily_data['time']):
            max_temp = daily_data['temperature_2m_max'][idx]
            min_temp = daily_data['temperature_2m_min'][idx]
            max_wind = daily_data['windspeed_10m_max'][idx]
            precip = daily_data['precipitation_sum'][idx]

            forecast_info += (f"Date: {date}\n"
                              f"Max Temperature: {max_temp}°C\n"
                              f"Min Temperature: {min_temp}°C\n"
                              f"Max Windspeed: {max_wind} km/h\n"
                              f"Precipitation: {precip} mm\n\n")
    else:
        logging.warning("No forecast data available.")
        forecast_info = "No forecast data available."
    
    return forecast_info
