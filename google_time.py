import requests
from datetime import datetime, timedelta

def get_google_time_hm():
    try:
        r = requests.get("https://www.google.com", timeout=5)
        gmt_time = r.headers['Date']

        dt = datetime.strptime(gmt_time, "%a, %d %b %Y %H:%M:%S %Z")
        ist_time = dt + timedelta(hours=5, minutes=30)

        return ist_time.time()

    except Exception:
        return None
