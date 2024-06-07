from datetime import timezone
from zoneinfo import ZoneInfo


def utc_to_local(utc_dt, local_timezone):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo(local_timezone))
