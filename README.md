# MatrixPortalWeatherPlusTime
Modified Adafruit MatrixPortal Weather to add Time.

Temperature and 24 hr clock are swapped every 10 seconds.

Most of the additions are in lines 107-120.  The time update was reduced from 1 hour to 10 minutes to keep the clock accurate without calling network.get_local_time() every minute (and stalling the display).  The only other additions to the code is the 'tunit' variable in the metric/imperial initialization section and dtemptime a couple lines before the main loop.  Conversion to 12 hour time would be simple, but there's no room for an AM/PM indicator during double-digit hours, so I left it at 24 hr time.

Coding the first version, I believed the MatrixPortal didn't have a real time clock function.  So I coded the minute and ten second counters using time.monotonic().  I knew it wasn't accurate, but I also knew calling network.get_local_time() stalls the display for several seconds - calling it every minute would be ugly and way overkill.  The biggest time sink was drilling into openweather_graphics.py and testing live updates of the displayed text variables.  While optimizing those and getting them to display correctly (apparently PortalBase does some formatting behind the scenes..), I finally saw it:  rtime = rtc.RTC()  Are you kidding me??  eesh... One whole section of the code wasn't needed any more, and optimizing the rest took no time at all.
