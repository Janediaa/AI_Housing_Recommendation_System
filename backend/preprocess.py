"""
Data Preprocessing & Geocoding Pipeline
========================================
Loads raw housing CSV, cleans columns, transforms facilities,
engineers features, geocodes locations, and saves processed dataset.
"""

import os
import sys
import time
import random
import requests
import numpy as np
import pandas as pd

# ============================================================
# GEOAPIFY API KEY — INSERT YOUR KEY HERE
# Get a free key at: https://myprojects.geoapify.com/register
# Free tier: 3,000 requests/day
# ============================================================
API_KEY = "f0eb9e82631f43e0933e430615efd8bb"

# Paths (relative to project root)
RAW_DATA_PATH = os.path.join("data", "raw", "housing_dataset_final.csv")
PROCESSED_DATA_PATH = os.path.join("data", "processed", "housing_processed.csv")
COORDS_CACHE_PATH = os.path.join("data", "processed", "location_coords.csv")

# All facility columns (after lowercasing)
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

# New engineered amenity columns
AMENITY_COLUMNS = [
    "airport_proximity",
    "school_proximity",
    "hospital_proximity",
    "mall_proximity",
    "metro_proximity"
]


def validate_api_key():
    """Ensure a valid Geoapify API key is set."""
    if API_KEY == "YOUR_GEOAPIFY_API_KEY" or not API_KEY or len(API_KEY) < 10:
        print("=" * 60)
        print("ERROR: Geoapify API key is not set!")
        print()
        print("Please edit backend/preprocess.py and replace:")
        print('  API_KEY = "YOUR_GEOAPIFY_API_KEY"')
        print("with your actual Geoapify API key.")
        print()
        print("Get a free key at:")
        print("  https://myprojects.geoapify.com/register")
        print("  (Free tier: 3,000 requests/day)")
        print("=" * 60)
        sys.exit(1)


def load_raw_data():
    """Load and return the raw CSV dataset."""
    print("[1/8] Loading raw dataset...")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def clean_columns(df):
    """Lowercase all column names and rename problematic ones."""
    print("[2/8] Cleaning column names...")
    df.columns = df.columns.str.lower().str.strip()

    # Rename specific columns
    rename_map = {}
    if "no. of bedrooms" in df.columns:
        rename_map["no. of bedrooms"] = "bhk"
    if "children'splayarea" in df.columns:
        rename_map["children'splayarea"] = "childrensplayarea"

    if rename_map:
        df = df.rename(columns=rename_map)
        print(f"  Renamed: {rename_map}")

    # Clean city column
    if "city" in df.columns:
        df["city"] = df["city"].str.lower().str.strip()
        null_count = df["city"].isnull().sum()
        if null_count > 0:
            print(f"  WARNING: {null_count} null city values found!")
            sys.exit(1)
        print(f"  Cities: {df['city'].unique().tolist()}")
    else:
        print("  ERROR: 'city' column not found in dataset!")
        sys.exit(1)

    return df


def transform_price(df):
    """Divide price by 100."""
    print("[3/8] Transforming price (÷100)...")
    df["price"] = df["price"] / 100
    print(f"  Price range: ₹{df['price'].min():,.0f} – ₹{df['price'].max():,.0f}")
    return df


def transform_facilities(df):
    """Replace ALL facility column values with random integers 0–5."""
    print("[4/8] Transforming facility columns to random 0–5...")
    np.random.seed(42)
    for col in FACILITY_COLUMNS:
        if col in df.columns:
            df[col] = np.random.randint(0, 6, size=len(df))
        else:
            print(f"  WARNING: facility column '{col}' not found, skipping")
    print(f"  Transformed {len(FACILITY_COLUMNS)} facility columns")
    return df


def add_amenity_columns(df):
    """Add 5 new engineered amenity proximity columns with random 0–5 values."""
    print("[5/8] Adding amenity proximity columns...")
    np.random.seed(123)
    for col in AMENITY_COLUMNS:
        df[col] = np.random.randint(0, 6, size=len(df))
        print(f"  Added '{col}' (mean: {df[col].mean():.2f})")
    return df


def handle_missing_values(df):
    """Handle missing values: area→median, bhk→mode, others→0."""
    print("[6/8] Handling missing values...")
    missing_before = df.isnull().sum().sum()

    if df["area"].isnull().any():
        median_area = df["area"].median()
        df["area"] = df["area"].fillna(median_area)
        print(f"  Filled area nulls with median: {median_area}")

    if df["bhk"].isnull().any():
        mode_bhk = df["bhk"].mode()[0]
        df["bhk"] = df["bhk"].fillna(mode_bhk)
        print(f"  Filled bhk nulls with mode: {mode_bhk}")

    # Fill remaining nulls with 0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    missing_after = df.isnull().sum().sum()
    print(f"  Missing values: {missing_before} → {missing_after}")
    return df


def engineer_features(df):
    """Create facility_score and price_per_sqft."""
    print("[7/8] Engineering features...")

    # facility_score = sum of all facility + amenity columns
    score_cols = [c for c in FACILITY_COLUMNS if c in df.columns] + \
                 [c for c in AMENITY_COLUMNS if c in df.columns]
    df["facility_score"] = df[score_cols].sum(axis=1)
    print(f"  facility_score: mean={df['facility_score'].mean():.1f}, "
          f"max={df['facility_score'].max()}")

    # price_per_sqft
    df["price_per_sqft"] = df["price"] / df["area"].replace(0, np.nan)
    df["price_per_sqft"] = df["price_per_sqft"].fillna(0)
    print(f"  price_per_sqft: mean={df['price_per_sqft'].mean():.1f}")

    return df


def geocode_location(location, city):
    """
    Geocode a single location using Geoapify API.

    Args:
        location: Area/locality name (e.g., "Saket")
        city: City name (e.g., "delhi")

    Returns:
        (latitude, longitude) tuple or (None, None) on failure
    """
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
            return result["lat"], result["lon"]
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"  Geocoding error for '{query}': {e}")
        return None, None


def geocode_all_locations(df):
    """
    Geocode all unique (location, city) pairs using Geoapify.
    Results are cached to avoid repeated API calls.
    """
    print("[8/8] Geocoding locations...")

    os.makedirs(os.path.dirname(COORDS_CACHE_PATH), exist_ok=True)

    # Load cache if exists
    cached = {}
    if os.path.exists(COORDS_CACHE_PATH):
        cache_df = pd.read_csv(COORDS_CACHE_PATH)
        for _, row in cache_df.iterrows():
            key = f"{row['location']}|{row['city']}"
            cached[key] = (row["latitude"], row["longitude"])
        print(f"  Loaded {len(cached)} cached coordinates")

    # Get unique (location, city) pairs
    unique_pairs = df[["location", "city"]].drop_duplicates()
    total = len(unique_pairs)
    print(f"  Total unique (location, city) pairs: {total}")

    # Geocode missing pairs
    new_count = 0
    failed_count = 0
    for idx, row in unique_pairs.iterrows():
        key = f"{row['location']}|{row['city']}"
        if key not in cached:
            lat, lng = geocode_location(row["location"], row["city"])
            if lat is not None and lng is not None:
                cached[key] = (lat, lng)
                new_count += 1
            else:
                failed_count += 1
                # Use city center approximations as last resort
                print(f"  FAILED to geocode: {row['location']}, {row['city']}")

            # Rate limiting: ~5 requests/second (Geoapify free tier)
            time.sleep(0.2)

            # Progress update every 50 locations
            done = new_count + failed_count
            cached_skip = total - (total - len([
                k for k in unique_pairs.itertuples()
                if f"{k.location}|{k.city}" not in cached or
                f"{k.location}|{k.city}" in cached
            ]))
            if done % 50 == 0 and done > 0:
                print(f"  Progress: {done} new geocoded, {failed_count} failed")

    print(f"  New geocoded: {new_count}, Failed: {failed_count}")

    # Save cache
    cache_rows = []
    for key, (lat, lng) in cached.items():
        location, city = key.split("|", 1)
        cache_rows.append({
            "location": location,
            "city": city,
            "latitude": lat,
            "longitude": lng
        })
    cache_df = pd.DataFrame(cache_rows)
    cache_df.to_csv(COORDS_CACHE_PATH, index=False)
    print(f"  Saved {len(cache_df)} coordinates to cache")

    # Merge coordinates into main dataframe
    coord_map = {}
    for key, (lat, lng) in cached.items():
        coord_map[key] = {"latitude": lat, "longitude": lng}

    df["latitude"] = df.apply(
        lambda r: coord_map.get(f"{r['location']}|{r['city']}", {}).get("latitude", np.nan),
        axis=1
    )
    df["longitude"] = df.apply(
        lambda r: coord_map.get(f"{r['location']}|{r['city']}", {}).get("longitude", np.nan),
        axis=1
    )

    # Report coverage
    has_coords = df["latitude"].notna().sum()
    print(f"  Coordinate coverage: {has_coords}/{len(df)} rows "
          f"({has_coords/len(df)*100:.1f}%)")

    # Drop rows without coordinates
    before = len(df)
    df = df.dropna(subset=["latitude", "longitude"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  Dropped {dropped} rows without coordinates")

    return df


def run_preprocessing():
    """Execute the full preprocessing pipeline."""
    print("=" * 60)
    print("HOUSING DATA PREPROCESSING PIPELINE")
    print("=" * 60)

    validate_api_key()

    df = load_raw_data()
    df = clean_columns(df)
    df = transform_price(df)
    df = transform_facilities(df)
    df = add_amenity_columns(df)
    df = handle_missing_values(df)
    df = engineer_features(df)
    df = geocode_all_locations(df)

    # Save processed dataset
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print()
    print("=" * 60)
    print(f"DONE! Saved processed dataset to: {PROCESSED_DATA_PATH}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Cities: {df['city'].unique().tolist()}")
    print("=" * 60)

    return df


if __name__ == "__main__":
    run_preprocessing()
