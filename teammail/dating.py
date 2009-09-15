# -*- coding: utf-8 -*-
from datetime import datetime, tzinfo, timedelta

class GMT_tzinfo(tzinfo):
    """Implementation of the Pacific timezone."""
    def utcoffset(self, dt):
        return timedelta(hours=0)

    def dst(self, dt):
        return timedelta(hours=0)

    def tzname(self, dt):
        return "GMT"

class Mountain_tzinfo(tzinfo):
    """Implementation of the Pacific timezone."""
    def utcoffset(self, dt):
        return timedelta(hours= -7) + self.dst(dt)

    def _FirstSunday(self, dt):
        """First Sunday on or after dt."""
        return dt + timedelta(days=(6 - dt.weekday()))

    def dst(self, dt):
        # 2 am on the second Sunday in March
        dst_start = self._FirstSunday(datetime(dt.year, 3, 8, 2))
        # 1 am on the first Sunday in November
        dst_end = self._FirstSunday(datetime(dt.year, 11, 1, 1))

        if dst_start <= dt.replace(tzinfo=None) < dst_end:
            return timedelta(hours=1)
        else:
            return timedelta(hours=0)

    def tzname(self, dt):
        if self.dst(dt) == timedelta(hours=0):
            return "MST"
        else:
            return "MDT"

GMT_tz = GMT_tzinfo()
Mountain_tz = Mountain_tzinfo()

def getLocalTime(utc_time=None):
    if utc_time:
        return utc_time.astimezone()
    else:
        return datetime.now().replace(tzinfo=GMT_tz).astimezone(Mountain_tz)
    
def embedLocalTimezone(input):
    return input.replace(tzinfo=Mountain_tz)
