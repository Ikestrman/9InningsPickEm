#This program was written to test pulling hourly weather data for the next 48 hours, for a specific lat/long.
#For now, 'lat' and 'lon' are hardcoded, but this will be replaced by a variable that contains the output
#from the GetSelectStadiums functionality, with a separate call being made for each Home team.

import requests
import json

api_key = "[redacted]"
lat = "33.441792"
lon = "-94.037689"
url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&exclude=minutely&appid=%s" % (lat, lon, api_key)

response = requests.get(url)
data = json.loads(response.text)
print(data)

#The example output for this program can be found in this GitHub directory, in OneCityWeatherExample.json.