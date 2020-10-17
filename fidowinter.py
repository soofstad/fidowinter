import requests
from time import sleep
from _datetime import datetime

from config import Config
from mail import send_email

lat = Config.FORECAST_COORDINATES["lat"]
long = Config.FORECAST_COORDINATES["long"]
url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={long}"


def main():
    print(datetime.now())
    print(f"Checking latest forecast...")
    req = requests.get(url)
    response = req.json()

    long_term_forecast = {}
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
    for forecast in response["properties"]["timeseries"]:

        long_term_forecast[forecast["time"]] = forecast["data"]["instant"]["details"]

        try:
            long_term_forecast[forecast["time"]]["precipitation_amount"] = forecast["data"]["next_6_hours"]["details"]["precipitation_amount"]
        except KeyError:
            try:
                long_term_forecast[forecast["time"]]["precipitation_amount"] = forecast["data"]["next_1_hours"]["details"]["precipitation_amount"]
            except KeyError:
                long_term_forecast[forecast["time"]]["precipitation_amount"] = None

    print(f"Forecast extends until {list(long_term_forecast.keys())[-1]}")

    date, forecast = first_sub_zero_day(long_term_forecast)
    if date:
        send_mail(date, forecast)
        print(f"There will be freezing temperatures on {date}")
        return

    print("No sub zero days in sight :)")


def send_mail(date, forecast):
    message = f"""
    Notification from FIDO - The First Day of Winter notifier
    There will be freezing temperatures on {date}.
    
    The forecast on that day is as follows;
        - Temperature: {forecast["air_temperature"]}
        - Precipitation: {forecast["precipitation_amount"]}
    """
    for email in Config.NOTIFICATION_SQUAD:
        send_email(sender=Config.EMAIL_SENDER, recipient=email, message_text=message)


def first_sub_zero_day(long_term_forecast):
    for k, v in long_term_forecast.items():
        if v["air_temperature"] < Config.TEMPERATURE_THRESHOLD:
            return k, v

    return None, None


if __name__ == "__main__":
    while True:
        main()
        sleep(86400)
