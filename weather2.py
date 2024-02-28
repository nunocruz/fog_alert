import openmeteo_requests

import smtplib
from email.message import EmailMessage
import requests_cache
import pandas as pd
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
  "hourly": ["temperature_2m", "dew_point_2m", "relative_humidity_2m", "weather_code"],
  "daily": "weather_code",
  "timezone": "Europe/Amsterdam",
  # "start_date": "2023-12-06",
  # "end_date": "2023-12-07"
  "forecast_days": 2
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()

hourly_time = range(hourly.Time(), hourly.TimeEnd(), hourly.Interval())
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()

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
hourly_data["fog"]=[]

# calculate fog information
for idx, temp in enumerate(hourly_temperature_2m):
  dew_point = round(hourly_data["dew_point_2m"][idx], 3)
  temperature = round(temp, 3)
  hourly_data["delta"].append(temperature - dew_point)

  if (temperature <= dew_point):
    hourly_data["fog"].append("Yes")
    print("YASS!!!\n") ## send the alert to me
  else:
    hourly_data["fog"].append("No")
    print("Nope!\n") ## send the alert to me

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)


# # Create a text/plain message
# msg = EmailMessage()
# msg['Subject'] = "FOG ALERT"
# msg['From'] = 'nuno.marques.cruz@gmail.com'
# msg['To'] = 'fog@nuno.aleeas.com'
# msg.set_content('fog')

# #Ports 465 and 587 are intended for email client to email server communication - sending email
# server = smtplib.SMTP('smtp.gmail.com', 587)
# server.ehlo()

# #starttls() is a way to take an existing insecure connection and upgrade it to a secure connection using SSL/TLS.
# server.starttls()

# #Next, log in to the server
# server.login("nuno.marques.cruz@gmail.com", "Trofa-Amsterdam-87-google")

# msg = "Hello! This Message was sent by the help of Python"

# #Send the mail
# server.send_message(msg)
# server.quit()
