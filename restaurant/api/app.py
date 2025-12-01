"""
REST API for Restaurant Analytics system.
Provides endpoints for review sentiment analysis, restaurant ratings, and NLP insights.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Restaurant Analytics API",
    description="API for restaurant review sentiment analysis and insights",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


class Review(BaseModel):
    """Review model"""

    review_id: Optional[str] = None
    restaurant_id: str
    rating: float = Field(ge=1, le=5, description="Rating 1-5 stars")
    text: str = Field(description="Review text")


class SentimentResponse(BaseModel):
    """Sentiment analysis response"""

    review_id: str
    sentiment: str
    polarity: float
    subjectivity: Optional[float] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Restaurant Analytics API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/restaurants",
            "/restaurants/{restaurant_id}",
            "/reviews",
            "/reviews/analyze",
            "/sentiment",
            "/stats",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "restaurant-analytics",
    }


@app.get("/restaurants")
async def get_restaurants(limit: int = Query(100, ge=1, le=1000)):
    """Get restaurant data"""
    try:
        restaurants_file = DATA_DIR / "restaurant_restaurants_clean.csv"

        if not restaurants_file.exists():
            raise HTTPException(status_code=404, detail="Restaurant data not found")

        df = pd.read_csv(restaurants_file)
        df = df.head(limit)

        return {"count": len(df), "restaurants": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants/{restaurant_id}")
async def get_restaurant(restaurant_id: str):
    """Get specific restaurant by ID"""
    try:
        restaurants_file = DATA_DIR / "restaurant_restaurants_clean.csv"

        if not restaurants_file.exists():
            raise HTTPException(status_code=404, detail="Restaurant data not found")

        df = pd.read_csv(restaurants_file)

        id_col = next(
            (
                col
                for col in df.columns
                if "restaurant" in col.lower() and "id" in col.lower()
            ),
            None,
        )

        if not id_col:
            raise HTTPException(
                status_code=500, detail="Restaurant ID column not found"
            )

        restaurant = df[df[id_col].astype(str) == restaurant_id]

        if len(restaurant) == 0:
            raise HTTPException(
                status_code=404, detail=f"Restaurant {restaurant_id} not found"
            )

        return restaurant.iloc[0].to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reviews")
async def get_reviews(
    limit: int = Query(100, ge=1, le=1000),
    restaurant_id: Optional[str] = None,
    min_rating: Optional[float] = None,
):
    """Get review data"""
    try:
        reviews_file = DATA_DIR / "restaurant_reviews_clean.csv"

        if not reviews_file.exists():
            raise HTTPException(status_code=404, detail="Review data not found")

        df = pd.read_csv(reviews_file)

        if restaurant_id:
            rest_col = next(
                (
                    col
                    for col in df.columns
                    if "restaurant" in col.lower() and "id" in col.lower()
                ),
                None,
            )
            if rest_col:
                df = df[df[rest_col].astype(str) == restaurant_id]

        if min_rating:
            rating_col = next(
                (
                    col
                    for col in df.columns
                    if "rating" in col.lower() or "stars" in col.lower()
                ),
                None,
            )
            if rating_col:
                df = df[df[rating_col] >= min_rating]

        df = df.head(limit)

        return {"count": len(df), "reviews": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reviews/analyze", response_model=SentimentResponse)
async def analyze_review(review: Review):
    """Analyze sentiment of a review"""
    try:
        # Simple sentiment analysis (replace with actual NLP model)
        text = review.text.lower()

        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "love",
            "best",
            "delicious",
        ]
        negative_words = ["bad", "terrible", "awful", "horrible", "worst", "disgusting"]

        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)

        polarity = (pos_count - neg_count) / max(pos_count + neg_count, 1)

        if polarity > 0.2:
            sentiment = "Positive"
        elif polarity < -0.2:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        return SentimentResponse(
            review_id=review.review_id or f"review_{datetime.now().timestamp()}",
            sentiment=sentiment,
            polarity=round(polarity, 3),
            subjectivity=0.5,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sentiment")
async def get_sentiment_data():
    """Get sentiment analysis results"""
    try:
        sentiment_file = DATA_DIR / "sentiment_analysis_results.csv"

        if sentiment_file.exists():
            df = pd.read_csv(sentiment_file)
            return {"count": len(df), "sentiment": df.to_dict(orient="records")}

        # Fallback to reviews with sentiment columns
        reviews_file = DATA_DIR / "restaurant_reviews_clean.csv"
        if reviews_file.exists():
            df = pd.read_csv(reviews_file)

            sentiment_cols = [col for col in df.columns if "sentiment" in col.lower()]
            if sentiment_cols:
                return {"count": len(df), "sentiment": df.to_dict(orient="records")}

        raise HTTPException(status_code=404, detail="Sentiment data not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get restaurant statistics"""
    try:
        stats = {"timestamp": datetime.now().isoformat()}

        # Restaurant stats
        restaurants_file = DATA_DIR / "restaurant_restaurants_clean.csv"
        if restaurants_file.exists():
            restaurants = pd.read_csv(restaurants_file)
            stats["total_restaurants"] = len(restaurants)

            rating_col = next(
                (col for col in restaurants.columns if "rating" in col.lower()), None
            )
            if rating_col:
                stats["avg_restaurant_rating"] = float(restaurants[rating_col].mean())

        # Review stats
        reviews_file = DATA_DIR / "restaurant_reviews_clean.csv"
        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)
            stats["total_reviews"] = len(reviews)

            rating_col = next(
                (
                    col
                    for col in reviews.columns
                    if "rating" in col.lower() or "stars" in col.lower()
                ),
                None,
            )
            if rating_col:
                stats["avg_review_rating"] = float(reviews[rating_col].mean())

            sentiment_col = next(
                (col for col in reviews.columns if "sentiment" in col.lower()), None
            )
            if sentiment_col:
                sentiment_dist = reviews[sentiment_col].value_counts().to_dict()
                stats["sentiment_distribution"] = sentiment_dist

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8006))
    uvicorn.run(app, host="0.0.0.0", port=port)
