# Matrix Weather display
# For Metro M4 Airlift with RGB Matrix shield, 64 x 32 RGB LED Matrix display

"""
This example queries the Open Weather Maps site API to find out the current
weather for your location... and display it on a screen!
if you can find something that spits out JSON data, we can display it
"""
import rtc
import time
import board
import microcontroller
from digitalio import DigitalInOut, Direction, Pull
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
import openweather_graphics  # pylint: disable=wrong-import-position

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

if hasattr(board, "D12"):
    jumper = DigitalInOut(board.D12)
    jumper.direction = Direction.INPUT
    jumper.pull = Pull.UP
    is_metric = jumper.value
elif hasattr(board, "BUTTON_DOWN") and hasattr(board, "BUTTON_UP"):
    button_down = DigitalInOut(board.BUTTON_DOWN)
    button_down.switch_to_input(pull=Pull.UP)

    button_up = DigitalInOut(board.BUTTON_UP)
    button_up.switch_to_input(pull=Pull.UP)
    if not button_down.value:
        print("Down Button Pressed")
        microcontroller.nvm[0] = 1
    elif not button_up.value:
        print("Up Button Pressed")
        microcontroller.nvm[0] = 0
    print(microcontroller.nvm[0])
    is_metric = microcontroller.nvm[0]
else:
    is_metric = False

if is_metric:
    UNITS = "metric"  # can pick 'imperial' or 'metric' as part of URL query
    tunit = "°C"
    print("Jumper set to metric")
else:
    UNITS = "imperial"
    tunit = "°F"
    print("Jumper set to imperial")

# Use cityname, country code where countrycode is ISO3166 format.
# E.g. "New York, US" or "London, GB"
LOCATION = "Charleston, US"
print("Getting weather for {}".format(LOCATION))
# Set up from where we'll be fetching data
DATA_SOURCE = (
    "http://api.openweathermap.org/data/2.5/weather?q=" + LOCATION + "&units=" + UNITS
)
DATA_SOURCE += "&appid=" + secrets["openweather_token"]
# You'll need to get a token from openweather.org, looks like 'b6907d289e10d714a6e88b30761fae22'
# it goes in your secrets.py file on a line such as:
# 'openweather_token' : 'your_big_humongous_gigantor_token',
DATA_LOCATION = []
SCROLL_HOLD_TIME = 0  # set this to hold each line before finishing scroll

# --- Display setup ---
matrix = Matrix()
network = Network(status_neopixel=board.NEOPIXEL, debug=True)
if UNITS == "imperial" or UNITS == "metric":
    gfx = openweather_graphics.OpenWeather_Graphics(
        matrix.display, am_pm=True, units=UNITS
    )

print("gfx loaded")
localtime_refresh = None
weather_refresh = None

rtime = rtc.RTC()

while True:
    # only query the online time once per hour (and on first run)
    if (not localtime_refresh) or (time.monotonic() - localtime_refresh) > 600:
        try:
            print("Getting time from internet!")
            network.get_local_time()
            ctime = rtime.datetime
            localtime_refresh = time.monotonic()
            # make next minute update very close to 00 seconds
            time_refresh = localtime_refresh - ctime.tm_sec
            dmins = int(ctime.tm_min)   # minute counter, since tm_min is read only
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    # only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        try:
            value = network.fetch_data(DATA_SOURCE, json_path=(DATA_LOCATION,))
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    # update time display, swap time and temp every ten seconds
    monotime = time.monotonic()
    dtemptime = (monotime // 10) % 2
    if (monotime - time_refresh) > 59:
        dmins += 1
        if dmins > 59:             # increment and check for overflow
            dmins = 0              # fix it
        time_refresh = monotime    # ready for next minute

    # tens digit even ->temp (dtemptime==True), odd->time (dtemptime==False)
    testvar = monotime // 10 % 2
    if dtemptime != monotime:     # changed?
        if dtemptime:             # if it was temp (even)..
            dtemptime = False     # it's now time
            gfx.temp_text.x = 16
            gfx.temp_text.text = f"{ctime.tm_hour}:{dmins:02}"
        else:
            dtemptime = True       # back to temperature
            gfx.temp_text.x = 20
            gfx.temp_text.text = f'{int(value["main"]["temp"])}{tunit}'

    gfx.scroll_next_label()
    # Pause between labels
    time.sleep(SCROLL_HOLD_TIME)