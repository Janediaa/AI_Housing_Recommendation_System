"""
Geolocation Utilities
======================
Geocoding via Geoapify API and Haversine distance calculations.
All distance computations are done locally — no API calls.
"""

import math
import requests

# ============================================================
# GEOAPIFY API KEY — INSERT YOUR KEY HERE
# Get a free key at: https://myprojects.geoapify.com/register
# Free tier: 3,000 requests/day
# ============================================================
API_KEY = "f0eb9e82631f43e0933e430615efd8bb"


def geocode_location(location, city):
    """
    Geocode a location using Geoapify API.

    Args:
        location: Area/locality name (e.g., "Saket")
        city: City name (e.g., "Delhi")

    Returns:
        dict with 'lat', 'lng', and 'city' keys

    Raises:
        ValueError: If API key is not set
        RuntimeError: If geocoding fails
    """
    if API_KEY == "YOUR_GEOAPIFY_API_KEY" or not API_KEY or len(API_KEY) < 10:
        raise ValueError(
            "Geoapify API key is not set! "
            "Edit backend/geo.py and replace API_KEY with your actual key. "
            "Get a free key at: https://myprojects.geoapify.com/register"
        )

    query = f"{location}, {city}, India"
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": query,
        "apiKey": API_KEY,
        "limit": 1,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            # Try to extract city from response
            detected_city = (
                result.get("city", "") or
                result.get("county", "") or
                city
            ).lower().strip()

            return {
                "lat": result["lat"],
                "lng": result["lon"],
                "city": detected_city,
                "formatted": result.get("formatted", query)
            }
        else:
            raise RuntimeError(
                f"No geocoding results found for '{query}'. "
                "Please check the location name and try again."
            )

    except requests.exceptions.RequestException as e:
        raise RuntimeError(
            f"Geocoding API request failed for '{query}': {str(e)}"
        )


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on Earth using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of point 1 (degrees)
        lat2, lon2: Latitude and longitude of point 2 (degrees)

    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_nearby(lat, lng, df, radius_km):
    """
    Find all locations in DataFrame within a given radius.

    Uses Haversine formula for distance calculation (no API calls).

    Args:
        lat: User's latitude
        lng: User's longitude
        df: DataFrame with 'latitude' and 'longitude' columns
        radius_km: Search radius in kilometers

    Returns:
        DataFrame with an added 'distance_km' column, filtered by radius,
        sorted by distance ascending.
    """
    df = df.copy()
    df["distance_km"] = df.apply(
        lambda row: haversine(lat, lng, row["latitude"], row["longitude"]),
        axis=1
    )
    nearby = df[df["distance_km"] <= radius_km].sort_values("distance_km")
    return nearby
