import requests
from time import sleep
from _datetime import datetime, timezone, timedelta

from config import Config
from mail import send_email

lat = Config.FORECAST_COORDINATES["lat"]
long = Config.FORECAST_COORDINATES["long"]
url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={long}"


def main():
    print(f"Starting run at {datetime.now()}")

    last_run = check_last_run()
    if (datetime.now() - last_run) < timedelta(days=1):
        print(f"Already ran at {last_run}")
        return

    print(f"Checking latest forecast...")
    req = requests.get(url)
    response = req.json()

    long_term_forecast = {}
    for forecast in response["properties"]["timeseries"]:

        long_term_forecast[forecast["time"]] = forecast["data"]["instant"]["details"]

        try:
            long_term_forecast[forecast["time"]]["precipitation_amount"] = forecast["data"]["next_6_hours"]["details"][
                "precipitation_amount"]
        except KeyError:
            try:
                long_term_forecast[forecast["time"]]["precipitation_amount"] = \
                forecast["data"]["next_1_hours"]["details"]["precipitation_amount"]
            except KeyError:
                long_term_forecast[forecast["time"]]["precipitation_amount"] = None

    print(f"Forecast extends until {list(long_term_forecast.keys())[-1]}")

    date, forecast = first_sub_zero_day(long_term_forecast)
    if date:
        as_datetime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        print(f"There will be temperatures below {Config.TEMPERATURE_THRESHOLD} on {date}")
        send_mail(as_datetime, forecast)

    write_last_run()


def send_mail(date: datetime, forecast):
    message = f"""
    Notification from FIDO - The First Day of Winter notifier
    There will be colder than {Config.TEMPERATURE_THRESHOLD} degrees celsius on {date.strftime('%d. %B %Y')}.
    That is {(date - datetime.now(tz=timezone.utc)).days} day(s) from now.
    
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


def write_last_run():
    with open("./.lastrun", "w") as file:
        file.write(str(datetime.now()))


def check_last_run():
    try:
        with open("./.lastrun", "r") as file:
            content = file.readline()
            return datetime.strptime(content, "%Y-%m-%d %H:%M:%S.%f")
    except FileNotFoundError:
        return datetime(year=2020, month=1, day=1)

if __name__ == "__main__":
    while True:
        main()
        print("Sleeping for 1 hour ...")
        sleep(3600)
