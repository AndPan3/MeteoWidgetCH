import openmeteo_requests
import pandas as pd
import json
import requests_cache
from geopy.exc import GeocoderServiceError
from retry_requests import retry
from geopy.geocoders import Nominatim
def GetWeather(Location):
    print("Weather Data by MeteoSwiss")
    geolocator = Nominatim(user_agent="And_pan3,ArchWidget,GitRepo,CH")

    try:
        location = geolocator.geocode(Location, timeout=30)
        if location:
            latitude = location.latitude
            longitude = location.longitude
        else:
            print("Location not found.")
            return None
    except GeocoderServiceError as e:
        print(f"Error connecting to the Geocoding API: {e}")
        return None

    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 3, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "weather_code", "wind_speed_10m", "cloud_cover"],
        "models": "meteoswiss_icon_ch1",
        "current":["temperature_2m", "is_day", "precipitation", "weather_code", "cloud_cover", "wind_speed_10m"],
        "forecast_days": 7,
    }
    responses = openmeteo.weather_api(url, params = params)
    response = responses[0]

    hourly = response.Hourly()
    htemp = hourly.Variables(0).ValuesAsNumpy()
    hprec = hourly.Variables(1).ValuesAsNumpy()
    hcode = hourly.Variables(2).ValuesAsNumpy()
    hwind = hourly.Variables(3).ValuesAsNumpy()
    hcloud = hourly.Variables(4).ValuesAsNumpy()
    current = response.Current()
    ctemp = current.Variables(0).Value()
    cday = current.Variables(1).Value()
    cprec = current.Variables(2).Value()
    ccode = current.Variables(3).Value()
    ccloud = current.Variables(4).Value()
    cwind = current.Variables(5).Value()
    return htemp, hprec, hcode, hwind, hcloud, ctemp, cday, cprec, ccode, ccloud, cwind
with open("zip.txt", "r") as file:
    location = file.read().strip()
Weather=GetWeather(location)
WeatherJson = {
    "Hourly": {
        "Temperature": htemp.tolist(),
        "Precipitation": hprec.tolist(),
        "WeatherCode": hcode.tolist(),
        "WindSpeed": hwind.tolist(),
        "CloudCover": hcloud.tolist()
    },
    "Current": {
        "Temperature": ctemp.tolist(),
        "IsDay": cday.tolist(),
        "Precipitation": cprec.tolist(),
        "WeatherCode": ccode.tolist(),
        "CloudCover": ccloud.tolist(),
        "WindSpeed": cwind.tolist()
    }}
print(WeatherJson)