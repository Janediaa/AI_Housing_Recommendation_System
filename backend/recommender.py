"""
Recommendation Engine
======================
City-isolated recommendations with ML predictions and scoring.
"""

import numpy as np
import pandas as pd
from backend.geo import haversine, find_nearby

CITIES = ["bangalore", "chennai", "delhi", "hyderabad", "kolkata", "mumbai"]
NUMERIC_FEATURES = [
    "area", "bhk", "latitude", "longitude", "facility_score",
    "airport_proximity", "school_proximity", "hospital_proximity",
    "mall_proximity", "metro_proximity"
]
FACILITY_COLUMNS = [
    "resale", "maintenancestaff", "gymnasium", "swimmingpool",
    "landscapedgardens", "joggingtrack", "rainwaterharvesting",
    "indoorgames", "shoppingmall", "intercom", "sportsfacility",
    "atm", "clubhouse", "school", "24x7security", "powerbackup",
    "carparking", "staffquarter", "cafeteria", "multipurposeroom",
    "hospital", "washingmachine", "gasconnection", "ac", "wifi",
    "childrensplayarea", "liftavailable", "bed", "vaastucompliant",
    "microwave", "golfcourse", "tv", "diningtable", "sofa",
    "wardrobe", "refrigerator"
]
AMENITY_COLUMNS = [
    "airport_proximity", "school_proximity", "hospital_proximity",
    "mall_proximity", "metro_proximity"
]


def match_city(detected_city):
    """Match detected city name to supported cities."""
    detected = detected_city.lower().strip()
    if detected in CITIES:
        return detected
    aliases = {
        "bengaluru": "bangalore", "bengaluru urban": "bangalore",
        "new delhi": "delhi", "navi mumbai": "mumbai",
        "thane": "mumbai", "greater mumbai": "mumbai",
        "calcutta": "kolkata", "madras": "chennai",
        "secunderabad": "hyderabad",
    }
    for alias, city in aliases.items():
        if alias in detected or detected in alias:
            return city
    for city in CITIES:
        if city in detected or detected in city:
            return city
    return None


def generate_synthetic_properties(nearby_df, user_lat, user_lng, n=8):
    """Generate synthetic property inputs from nearby data."""
    if len(nearby_df) == 0:
        return []
    np.random.seed(None)
    n = min(n, max(5, len(nearby_df)))
    properties = []
    for i in range(n):
        base = nearby_df.sample(1).iloc[0]
        area_var = np.random.uniform(0.85, 1.15)
        prop = {
            "area": int(base["area"] * area_var),
            "bhk": int(base["bhk"]),
            "latitude": base["latitude"] + np.random.uniform(-0.005, 0.005),
            "longitude": base["longitude"] + np.random.uniform(-0.005, 0.005),
            "facility_score": max(0, int(base.get("facility_score", 0) + np.random.randint(-5, 6))),
            "airport_proximity": int(np.clip(base.get("airport_proximity", 2) + np.random.randint(-1, 2), 0, 5)),
            "school_proximity": int(np.clip(base.get("school_proximity", 3) + np.random.randint(-1, 2), 0, 5)),
            "hospital_proximity": int(np.clip(base.get("hospital_proximity", 3) + np.random.randint(-1, 2), 0, 5)),
            "mall_proximity": int(np.clip(base.get("mall_proximity", 2) + np.random.randint(-1, 2), 0, 5)),
            "metro_proximity": int(np.clip(base.get("metro_proximity", 2) + np.random.randint(-1, 2), 0, 5)),
            "location": base.get("location", "Unknown"),
            "city": base.get("city", "unknown"),
        }
        prop["distance_km"] = haversine(user_lat, user_lng, prop["latitude"], prop["longitude"])
        properties.append(prop)
    return properties


def predict_prices(properties, model, scaler, feature_columns):
    """Run model predictions on synthetic properties."""
    if not properties:
        return []
    rows = []
    for prop in properties:
        row = {feat: prop.get(feat, 0) for feat in NUMERIC_FEATURES}
        city = prop.get("city", "").lower().strip()
        for c in CITIES:
            row[f"city_{c}"] = 1 if city == c else 0
        rows.append(row)
    df = pd.DataFrame(rows)
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_columns]
    df_scaled = df.copy()
    df_scaled[NUMERIC_FEATURES] = scaler.transform(df[NUMERIC_FEATURES])
    predictions = model.predict(df_scaled)
    return predictions.tolist()


def compute_score(prop, predicted_price, user_budget, user_facilities):
    """Compute recommendation score 0-10."""
    # Budget fit
    if user_budget > 0:
        ratio = predicted_price / user_budget
        budget_fit = 1.0 if ratio <= 1.0 else max(0, 1.0 - (ratio - 1.0) * 2) if ratio <= 1.5 else 0.0
    else:
        budget_fit = 0.5
    budget_fit = max(0, min(1, budget_fit))

    # Distance score
    d = prop.get("distance_km", 0)
    if d <= 1:
        dist_score = 1.0
    elif d <= 5:
        dist_score = 1.0 - (d - 1) / 4 * 0.3
    elif d <= 15:
        dist_score = 0.7 - (d - 5) / 10 * 0.4
    else:
        dist_score = max(0, 0.3 - (d - 15) / 20 * 0.3)
    dist_score = max(0, min(1, dist_score))

    # Facility match
    if user_facilities and len(user_facilities) > 0:
        match_count = 0
        for fac in user_facilities:
            fac_key = fac.lower().replace(" ", "").replace("_", "")
            for col in FACILITY_COLUMNS + AMENITY_COLUMNS:
                col_clean = col.lower().replace("_", "")
                if fac_key in col_clean or col_clean in fac_key:
                    if prop.get(col, 0) >= 3:
                        match_count += 1
                    break
        fac_match = match_count / len(user_facilities)
    else:
        fac_match = 0.5
    fac_match = max(0, min(1, fac_match))

    # Area fit
    area = prop.get("area", 0)
    if area > 0 and predicted_price > 0:
        pps = predicted_price / area
        area_fit = 1.0 if pps < 50 else 0.8 if pps < 100 else 0.5 if pps < 200 else max(0, 1.0 - pps / 500)
    else:
        area_fit = 0.5
    area_fit = max(0, min(1, area_fit))

    raw = 0.4 * budget_fit + 0.3 * dist_score + 0.2 * fac_match + 0.1 * area_fit
    return round(raw * 10, 1)


def generate_recommendations(
    user_lat, user_lng, user_city, user_budget, user_radius,
    user_facilities, df, model, scaler, feature_columns
):
    """Full recommendation pipeline with city-level isolation."""
    # Step 1: City isolation
    city_df = df[df["city"] == user_city].copy()
    if len(city_df) == 0:
        return {"recommendations": [], "message": f"No data for city: {user_city}"}

    # Step 2: Nearby properties
    nearby = find_nearby(user_lat, user_lng, city_df, user_radius)
    if len(nearby) == 0:
        nearby = find_nearby(user_lat, user_lng, city_df, user_radius * 2)
        if len(nearby) == 0:
            return {
                "recommendations": [],
                "message": f"No properties within {user_radius}km. Try a larger radius."
            }

    # Step 3: Synthetic properties
    synthetic = generate_synthetic_properties(nearby, user_lat, user_lng, n=8)
    if not synthetic:
        return {"recommendations": [], "message": "Could not generate recommendations."}

    # Step 4: Predict
    prices = predict_prices(synthetic, model, scaler, feature_columns)

    # Step 5: Score and build response
    recs = []
    for prop, price in zip(synthetic, prices):
        score = compute_score(prop, price, user_budget, user_facilities)
        highlights = []
        if price <= user_budget:
            highlights.append("Within Budget")
        if prop.get("distance_km", 99) <= 3:
            highlights.append("Close Location")
        if prop.get("facility_score", 0) >= 80:
            highlights.append("Rich Amenities")
        if prop.get("metro_proximity", 0) >= 4:
            highlights.append("Near Metro")
        if prop.get("hospital_proximity", 0) >= 4:
            highlights.append("Near Hospital")
        if score >= 7:
            highlights.append("Highly Recommended")

        recs.append({
            "price": round(price, 0),
            "distance": round(prop.get("distance_km", 0), 2),
            "bhk": int(prop.get("bhk", 2)),
            "area": int(prop.get("area", 0)),
            "facility_score": int(prop.get("facility_score", 0)),
            "score": score,
            "lat": round(prop.get("latitude", 0), 6),
            "lng": round(prop.get("longitude", 0), 6),
            "city": prop.get("city", user_city),
            "location": prop.get("location", "Unknown"),
            "highlights": highlights,
            "amenities": {
                "airport": int(prop.get("airport_proximity", 0)),
                "school": int(prop.get("school_proximity", 0)),
                "hospital": int(prop.get("hospital_proximity", 0)),
                "mall": int(prop.get("mall_proximity", 0)),
                "metro": int(prop.get("metro_proximity", 0)),
            }
        })

    recs.sort(key=lambda x: x["score"], reverse=True)
    return {
        "recommendations": recs,
        "message": f"Found {len(recs)} recommendations in {user_city.title()}"
    }
