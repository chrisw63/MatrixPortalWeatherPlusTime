# MatrixPortalWeatherPlusTime
Modified Adafruit MatrixPortal Weather to add Time.

Every 10 seconds, the temperature is replaced with the 24 hr clock.

Most of my additions are in lines 111-130.  The time update was reduced from 1 hour to 10 minutes to keep the clock accurate without calling network.get_local_time() every minute.  Minute tracking within that ten minutes is.. basic, but it works.  The only other additions to the code is the 'tunit' variable in the metric/imperial initialization section and the ctime, time_refresh and dmins variables in the time update section.  Conversion to 12 hour time would be simple, but there's no room for an AM/PM indicator during double-digit hours, so I left it at 24 hr time.
