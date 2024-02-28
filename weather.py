import requests
import json

weather_request = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&minutely_15=temperature_2m,dewpoint_2m,cloudcover_low,visibility&timezone=Europe%2FBerlin&forecast_days=1"
response = requests.get(weather_request)

data = json.loads(response.content)
print(json.dumps(data, indent=2))


# is temperature below dew point? 

# low cloud coverage? Above 50%?

# WMO Weather interpretation codes (WW)
# 45, 48

