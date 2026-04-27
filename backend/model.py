"""
ML Model Training Pipeline
============================
Trains an XGBoost regressor (with Random Forest fallback) on
preprocessed housing data. Saves model, scaler, and feature columns.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

# Paths
PROCESSED_DATA_PATH = os.path.join("data", "processed", "housing_processed.csv")
MODELS_DIR = os.path.join("backend", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "price_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
FEATURE_COLS_PATH = os.path.join(MODELS_DIR, "feature_columns.pkl")

# Numeric features for scaling
NUMERIC_FEATURES = [
    "area", "bhk", "latitude", "longitude", "facility_score",
    "airport_proximity", "school_proximity", "hospital_proximity",
    "mall_proximity", "metro_proximity"
]

# Cities for one-hot encoding
CITIES = ["bangalore", "chennai", "delhi", "hyderabad", "kolkata", "mumbai"]


def load_processed_data():
    """Load the preprocessed dataset."""
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"ERROR: Processed data not found at '{PROCESSED_DATA_PATH}'")
        print("Run 'python backend/preprocess.py' first.")
        sys.exit(1)

    df = pd.read_csv(PROCESSED_DATA_PATH)
    print(f"Loaded {len(df)} rows from processed dataset")
    return df


def prepare_features(df):
    """Prepare feature matrix with numeric features + one-hot encoded city."""
    print("\nPreparing features...")

    # Verify numeric features exist
    missing = [f for f in NUMERIC_FEATURES if f not in df.columns]
    if missing:
        print(f"ERROR: Missing feature columns: {missing}")
        sys.exit(1)

    # One-hot encode city
    for city in CITIES:
        col_name = f"city_{city}"
        df[col_name] = (df["city"] == city).astype(int)

    city_cols = [f"city_{c}" for c in CITIES]
    all_features = NUMERIC_FEATURES + city_cols

    print(f"  Numeric features: {len(NUMERIC_FEATURES)}")
    print(f"  City one-hot columns: {len(city_cols)}")
    print(f"  Total features: {len(all_features)}")
    print(f"  Feature names: {all_features}")

    X = df[all_features].copy()
    y = df["price"].copy()

    # Remove invalid rows
    valid_mask = y > 0
    X = X[valid_mask]
    y = y[valid_mask]

    print(f"  Valid samples: {len(X)}")

    return X, y, all_features


def train_model(X_train, y_train, X_test, y_test):
    """Train XGBoost regressor with Random Forest fallback."""

    model = None

    # Try XGBoost first
    try:
        from xgboost import XGBRegressor
        print("\nTraining XGBoost Regressor...")
        model = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbosity=1
        )
        model.fit(X_train, y_train)
        print("  XGBoost training complete!")

    except ImportError:
        print("\nWARNING: XGBoost not available, falling back to Random Forest...")
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        print("  Random Forest training complete!")

    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)

    print("\n" + "=" * 50)
    print("MODEL EVALUATION RESULTS")
    print("=" * 50)
    print(f"  Train MAE:  ₹{train_mae:,.0f}")
    print(f"  Test  MAE:  ₹{test_mae:,.0f}")
    print(f"  Train R²:   {train_r2:.4f}")
    print(f"  Test  R²:   {test_r2:.4f}")
    print("=" * 50)

    return model


def run_training():
    """Execute the full training pipeline."""
    print("=" * 60)
    print("ML MODEL TRAINING PIPELINE")
    print("=" * 60)

    # Load data
    df = load_processed_data()

    # Prepare features
    X, y, feature_columns = prepare_features(df)

    # Scale numeric features
    print("\nApplying StandardScaler to numeric features...")
    scaler = StandardScaler()
    X_scaled = X.copy()
    X_scaled[NUMERIC_FEATURES] = scaler.fit_transform(X[NUMERIC_FEATURES])
    print("  Scaling complete.")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    print(f"\nTrain/Test split: {len(X_train)} / {len(X_test)}")

    # Train model
    model = train_model(X_train, y_train, X_test, y_test)

    # Save artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved model to: {MODEL_PATH}")

    joblib.dump(scaler, SCALER_PATH)
    print(f"Saved scaler to: {SCALER_PATH}")

    joblib.dump(feature_columns, FEATURE_COLS_PATH)
    print(f"Saved feature columns to: {FEATURE_COLS_PATH}")

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    run_training()
