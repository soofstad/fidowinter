import requests
import json
from time import sleep
from _datetime import datetime

latitude = 60.10
longtitude = 9.58
temperature_trigger = 0.5
url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longtitude}"

def main():
    print(datetime.now())
    print(f"Checking latest forcast...")
    req = requests.get(url)
    response = json.load(req.json())

    long_term_forcast = {}
    """
    {
        time_string: {
            air_pressure_at_sea_level,
            air_temperature,
            cloud_area_fraction,
            relative_humidity,
            wind_from_direction,
            wind_speed
        }
    }
    """
    for forcast in response["properties"]["timeseries"]:
        long_term_forcast[forcast["time"]] = forcast["data"]["instant"]["details"]

    print(f"Forcast extends until {long_term_forcast.keys[-1]}")

    date, forcast = first_sub_zero_day(long_term_forcast)
    if date:
        send_mail(date, forcast)
        print(f"There will be freezing temperatures on {date}")
        return

    print("No sub zero days in sight :)")

def send_mail(date, forcast):
    raise NotImplementedError

def first_sub_zero_day(long_term_forcast):
    for k, v in long_term_forcast.items():
        if v["air_temperature"] < temperature_trigger:
            return k, v
    return None, None


if __name__ == "__main__":
    while True:
        main()
        sleep(86400)
