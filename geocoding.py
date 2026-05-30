import os
import requests


def geocode_address(address, city):
    api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")

    if not api_key:
        return None, None

    full_address = f"{address}, {city}, Italia"

    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={
            "address": full_address,
            "key": api_key,
            "region": "it"
        },
        timeout=10
    )

    data = response.json()

    print("FULL ADDRESS:", full_address)
    print("GEOCODING STATUS:", data.get("status"))
    print("GEOCODING ERROR:", data.get("error_message"))

    if data.get("status") != "OK":
        print("Geocoding error:", data.get("status"), data.get("error_message"))
        return None, None

    location = data["results"][0]["geometry"]["location"]

    return location["lat"], location["lng"]