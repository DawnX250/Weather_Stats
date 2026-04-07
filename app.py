from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime, time
from aqi import simple_aqi
from google_time import get_google_time_hm

app = Flask(__name__)
app.secret_key="keyisverygood"

API_KEY="e63f2a2010604c32965160516253011"
API_URL="http://api.weatherapi.com/v1"


def map_condition_to_icon(cond):
    now = get_google_time_hm()
    night_start = time(19, 0)
    night_end = time(5, 0)

    cond = cond.lower().strip()
    is_night = (now >= night_start or now <= night_end)

    if "clear" in cond:
        return "night" if is_night else "sunny"

    if "sunny" in cond:
        return "sunny"

    if "partly" in cond:
        return "partly-cloudy"

    if any(x in cond for x in ["cloud", "cloudy", "overcast"]):
        return "cloudy"
    
    if any(x in cond for x in ["rain", "drizzle", "shower"]):
        return "rain"

    if any(x in cond for x in ["thunder", "storm", "thundery"]):
        return "thunder"

    if any(x in cond for x in ["snow", "sleet", "blizzard", "ice"]):
        return "snow"

    if any(x in cond for x in ["fog", "mist", "haze", "smoke"]):
        return "mist"
    return "cloudy"


def map_condition_to_video(cond, is_day):
    cond = cond.lower().strip()

    if any(x in cond for x in ["rain", "drizzle", "shower"]):
        return "rain_video.mp4"

    if any(x in cond for x in ["snow", "sleet", "blizzard", "ice"]):
        return "snow_video.mp4"

    if any(x in cond for x in ["thunder", "storm", "thundery"]):
        return "thunder_video.mp4"

    if any(x in cond for x in ["cloud", "cloudy", "overcast", "partly"]):
        return "clouds_video.mp4"

    if any(x in cond for x in ["mist", "fog", "haze", "smoke"]):
        return "mist_video.mp4"

    if "clear" in cond:
        return "sunny_video.mp4" if is_day else "night_video.mp4"

    return "sunny_video.mp4"


def format_date(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%d-%m-%Y")
    except:
        return date_str


@app.route("/", methods=["GET","POST"])
def home():
    if request.method=="POST":
        city = request.form.get("city","").strip()
        if city:
            return redirect(url_for("home", city=city))
        else:
            return render_template("index.html", weather=None, error="Please enter a city name.", bg_video="clouds_video.mp4")

    city = request.args.get("city")
    weather = None
    error = None
    bg_video = "clouds_video.mp4" 

    if city:
        try:
            url = f"{API_URL}/forecast.json?key={API_KEY}&q={city}&aqi=yes&days=4"
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()

            if "error" in data:
                error = data["error"].get("message","Unknown API error")
            else:
                loc = data["location"]["name"]
                cur = data["current"]
                cond = cur["condition"]["text"]
                is_day = cur.get("is_day",1)==1

                bg_video = map_condition_to_video(cond, is_day)

                epa_aqi = cur["air_quality"].get("us-epa-index", None)
                pm25 = cur["air_quality"].get("pm2_5", None)

                if pm25 is not None:
                    suggestion = simple_aqi(pm25)
                else:
                    suggestion = "AQI data not available"

                if epa_aqi is None:
                    aqi_display = "AQI data not available"
                else:
                    aqi_display = f"{suggestion}"

                fc = data["forecast"]["forecastday"]

                weather = {
                    "location": loc,
                    "condition": cond,
                    "icon": map_condition_to_icon(cond),
                    "temp": round(cur["temp_c"]),
                    "feels": round(cur["feelslike_c"]),
                    "humidity": cur["humidity"],
                    "pressure": round(cur["pressure_mb"]),
                    "visibility": cur["vis_km"],
                    "wind": round(cur["wind_kph"]),
                    "cloud": cur["cloud"],
                    "uv": cur["uv"],
                    "aqi": aqi_display,
                    "forecast": []
                }

                for d in fc:
                    fcond = d["day"]["condition"]["text"]
                    weather["forecast"].append({
                        "date": format_date(d["date"]),
                        "sunrise": d["astro"]["sunrise"],
                        "sunset": d["astro"]["sunset"],
                        "avg": round(d["day"]["avgtemp_c"]),
                        "max": round(d["day"]["maxtemp_c"]),
                        "min": round(d["day"]["mintemp_c"]),
                        "humidity": d["day"]["avghumidity"],
                        "rain": d["day"]["daily_chance_of_rain"],
                        "icon": map_condition_to_icon(fcond)
                    })

        except:
            error = "An unexpected error occurred."

    return render_template("index.html",
        weather=weather,
        error=error,
        bg_video=bg_video
    )


if __name__=="__main__":
    app.run(debug=True)
