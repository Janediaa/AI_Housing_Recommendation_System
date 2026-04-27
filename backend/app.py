"""
FastAPI Backend Application
============================
Serves housing recommendations via REST API.
"""

import os
import sys
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.geo import geocode_location
from backend.recommender import generate_recommendations, match_city

# ─── App Setup ───────────────────────────────────────────────
app = FastAPI(
    title="AI Housing Recommendation System",
    description="ML-powered housing recommendations across Indian metro cities",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Paths ───────────────────────────────────────────────────
PROCESSED_DATA_PATH = os.path.join("data", "processed", "housing_processed.csv")
MODEL_PATH = os.path.join("backend", "models", "price_model.pkl")
SCALER_PATH = os.path.join("backend", "models", "scaler.pkl")
FEATURE_COLS_PATH = os.path.join("backend", "models", "feature_columns.pkl")

# ─── Global State ────────────────────────────────────────────
model = None
scaler = None
feature_columns = None
housing_df = None


# ─── Request/Response Models ────────────────────────────────
class RecommendRequest(BaseModel):
    location: str = Field(..., description="Area/locality name")
    budget: float = Field(..., description="Budget in INR", gt=0)
    radius: float = Field(default=10.0, description="Search radius in km", gt=0)
    facilities: List[str] = Field(default=[], description="Preferred facility names")


class AmenityDetail(BaseModel):
    airport: int = 0
    school: int = 0
    hospital: int = 0
    mall: int = 0
    metro: int = 0


class RecommendationItem(BaseModel):
    price: float
    distance: float
    bhk: int
    area: int
    facility_score: int
    score: float
    lat: float
    lng: float
    city: str
    location: str
    highlights: List[str]
    amenities: AmenityDetail


class RecommendResponse(BaseModel):
    recommendations: List[RecommendationItem]
    message: str


# ─── Startup ─────────────────────────────────────────────────
@app.on_event("startup")
def load_artifacts():
    """Load model, scaler, feature columns, and processed data at startup."""
    global model, scaler, feature_columns, housing_df

    # Check files exist
    missing = []
    for path, name in [
        (PROCESSED_DATA_PATH, "Processed data"),
        (MODEL_PATH, "Model"),
        (SCALER_PATH, "Scaler"),
        (FEATURE_COLS_PATH, "Feature columns"),
    ]:
        if not os.path.exists(path):
            missing.append(f"  {name}: {path}")

    if missing:
        print("=" * 60)
        print("ERROR: Required files not found:")
        for m in missing:
            print(m)
        print()
        print("Run these commands first:")
        print("  python backend/preprocess.py")
        print("  python backend/model.py")
        print("=" * 60)
        sys.exit(1)

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    feature_columns = joblib.load(FEATURE_COLS_PATH)
    housing_df = pd.read_csv(PROCESSED_DATA_PATH)

    print("=" * 60)
    print("AI Housing Recommendation System - Backend Started")
    print(f"  Dataset: {len(housing_df)} properties")
    print(f"  Cities: {housing_df['city'].unique().tolist()}")
    print(f"  Features: {len(feature_columns)}")
    print(f"  Model: {type(model).__name__}")
    print("=" * 60)


# ─── Endpoints ───────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "AI Housing Recommendation System",
        "version": "1.0.0",
        "endpoints": {
            "POST /recommend": "Get housing recommendations"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "data_loaded": housing_df is not None,
        "cities": housing_df["city"].unique().tolist() if housing_df is not None else []
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """
    Get housing recommendations for a location.

    1. Geocodes the input location
    2. Determines the city
    3. Filters dataset by city
    4. Finds nearby properties
    5. Generates synthetic inputs and predicts prices
    6. Scores and ranks recommendations
    """
    if not model or housing_df is None:
        raise HTTPException(status_code=503, detail="Service not ready. Model not loaded.")

    # Parse location and city from input
    # User can enter "Saket, Delhi" or just "Saket"
    parts = [p.strip() for p in req.location.split(",")]
    if len(parts) >= 2:
        location_name = parts[0]
        city_input = parts[1]
    else:
        location_name = parts[0]
        city_input = ""

    # Geocode the location
    try:
        geo_result = geocode_location(location_name, city_input if city_input else location_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

    user_lat = geo_result["lat"]
    user_lng = geo_result["lng"]
    detected_city = geo_result["city"]

    # Match to supported city
    user_city = match_city(detected_city)
    if city_input:
        # Prefer user-specified city if valid
        matched_input = match_city(city_input)
        if matched_input:
            user_city = matched_input

    if not user_city:
        raise HTTPException(
            status_code=400,
            detail=(
                f"City '{detected_city}' is not supported. "
                f"Supported cities: Bangalore, Chennai, Delhi, Hyderabad, Kolkata, Mumbai. "
                f"Please include the city name, e.g., 'Saket, Delhi'."
            )
        )

    # Generate recommendations
    result = generate_recommendations(
        user_lat=user_lat,
        user_lng=user_lng,
        user_city=user_city,
        user_budget=req.budget,
        user_radius=req.radius,
        user_facilities=req.facilities,
        df=housing_df,
        model=model,
        scaler=scaler,
        feature_columns=feature_columns
    )

    return RecommendResponse(
        recommendations=result["recommendations"],
        message=result["message"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
