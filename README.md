# AI Housing Recommendation System

ML-powered housing recommendation engine for Indian metro cities. Uses XGBoost to predict property prices and generates personalized recommendations based on location, budget, distance, and facility preferences.

## Supported Cities

- Delhi
- Mumbai
- Bangalore
- Chennai
- Kolkata
- Hyderabad

## Tech Stack

| Layer    | Technology                          |
| -------- | ----------------------------------- |
| Frontend | React (Vite) + Tailwind CSS v4 + Leaflet.js |
| Backend  | Python FastAPI                      |
| ML Model | XGBoost Regressor (scikit-learn)    |
| Geocoding| Geoapify (free tier)                |
| Maps     | OpenStreetMap + Leaflet.js          |

## Prerequisites

- Python 3.10+
- Node.js 18+
- Geoapify API key (free) — [Get one here](https://myprojects.geoapify.com/register)

## Setup Instructions

### 1. Clone and Navigate

```bash
cd housing-ai
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Your Geoapify API Key

Open these two files and replace `YOUR_GEOAPIFY_API_KEY` with your actual key:

- `backend/preprocess.py` (line ~20)
- `backend/geo.py` (line ~14)

```python
API_KEY = "your_actual_api_key_here"
```

> **Free tier**: 3,000 requests/day — sufficient for preprocessing and runtime.

### 4. Run Data Preprocessing

```bash
python backend/preprocess.py
```

This will:
- Clean and transform the dataset
- Geocode all 1,776 unique locations (one-time, cached)
- Save processed data to `data/processed/housing_processed.csv`

> **Note**: First run takes ~10 minutes due to geocoding. Subsequent runs use cached coordinates.

### 5. Train the ML Model

```bash
python backend/model.py
```

This will:
- Train an XGBoost regressor on the processed data
- Print MAE and R² evaluation metrics
- Save model artifacts to `backend/models/`

### 6. Start the Backend

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### 7. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

## API Documentation

### POST /recommend

**Request:**
```json
{
  "location": "Saket, Delhi",
  "budget": 5000000,
  "radius": 10,
  "facilities": ["Gymnasium", "Car Parking", "Metro Proximity"]
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "price": 4500000,
      "distance": 2.5,
      "bhk": 3,
      "area": 1200,
      "facility_score": 85,
      "score": 8.2,
      "lat": 28.5244,
      "lng": 77.2066,
      "city": "delhi",
      "location": "Saket",
      "highlights": ["Within Budget", "Close Location", "Highly Recommended"],
      "amenities": {
        "airport": 2,
        "school": 4,
        "hospital": 5,
        "mall": 3,
        "metro": 4
      }
    }
  ],
  "message": "Found 8 recommendations in Delhi"
}
```

### GET /health

Returns system health status and loaded cities.

## Project Structure

```
housing-ai/
├── data/
│   ├── raw/
│   │   └── housing_dataset_final.csv
│   └── processed/
│       ├── housing_processed.csv
│       └── location_coords.csv
├── backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── model.py             # ML training pipeline
│   ├── recommender.py       # Recommendation engine
│   ├── geo.py               # Geocoding & Haversine
│   ├── preprocess.py        # Data preprocessing
│   └── models/
│       ├── price_model.pkl
│       ├── scaler.pkl
│       └── feature_columns.pkl
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputPanel.jsx
│   │   │   ├── MapView.jsx
│   │   │   └── RecommendationCard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   └── package.json
├── requirements.txt
└── README.md
```

## Recommendation Scoring

Each property receives a score (0–10) based on:

| Component      | Weight | Description                        |
| -------------- | ------ | ---------------------------------- |
| Budget Fit     | 40%    | How well the price fits the budget |
| Distance Score | 30%    | Proximity to searched location     |
| Facility Match | 20%    | Match with user's preferences      |
| Area Fit       | 10%    | Value per square foot              |

## Geoapify API Details

- **Endpoint**: `https://api.geoapify.com/v1/geocode/search`
- **Format**: `?text={location},{city},India&apiKey={key}&limit=1&format=json`
- **Rate Limit**: Free tier — 3,000 requests/day, 5 requests/second
- **Usage**: Geocoding user input locations at runtime + one-time dataset preprocessing

