def simple_aqi(pm):
    if pm<=30: return f"AQI(50): Good"
    elif pm<=60: return f"AQI(100): Moderate"
    elif pm<=90: return f"AQI(150): Unhealthy for Sensitive Groups"
    elif pm<=120: return f"AQI(200): Unhealthy"
    elif pm<=250: return f"AQI(300): Very Unhealthy"
    else: return f"AQI(400): Hazardous"