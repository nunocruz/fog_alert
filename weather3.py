import openmeteo_requests

import pandas as pd
import requests_cache
import sys
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.37403,
	"longitude": 4.88969,
	"current": ["temperature_2m", "weather_code"],
	"hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "weather_code", "cloud_cover_low"],
	"daily": "weather_code",
	"timezone": "Europe/Berlin",
	"forecast_days": sys.argv[1]
	
}
responses = openmeteo.weather_api(url, params=params)

print("")
# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_weather_code = current.Variables(1).Value()

print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}")
print(f"Current weather_code {current_weather_code}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(3).ValuesAsNumpy()
hourly_cloud_cover_low = hourly.Variables(4).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s"),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["dew_point_2m"] = hourly_dew_point_2m
hourly_data["delta"] = []
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["weather_code"] = hourly_weather_code
hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
hourly_data["fog"]=[]

fog_information=[]

# calculate fog information
for idx, temp in enumerate(hourly_temperature_2m): 
  dew_point = round(hourly_data["dew_point_2m"][idx], 3)
  temperature = round(temp, 3)
  hourly_data["delta"].append(temperature - dew_point)
  weather_code = hourly_data["weather_code"][idx]

  if (temperature <= dew_point or weather_code == 45 or weather_code == 48):
    hourly_data["fog"].append("Yes")
    fog_information.append("Fog at: " + str(hourly_data["date"][idx]))
  else:
    hourly_data["fog"].append("No")

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe.to_string())
print("")

for fog_timestamp in fog_information: 
	print(fog_timestamp) ##if this shit is not empty send an email