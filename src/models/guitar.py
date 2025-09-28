from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Guitar(BaseModel):
    """Guitar listing model"""
    title: str
    price: float
    condition: str = "Unknown"
    image_url: Optional[str] = None
    link: Optional[str] = None
    source: str = "Unknown"
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Fender Stratocaster American Professional II",
                "price": 1699.99,
                "condition": "Excellent",
                "image_url": "https://example.com/guitar.jpg",
                "link": "https://reverb.com/item/123456",
                "source": "Reverb",
                "brand": "Fender",
                "model": "Stratocaster",
                "year": 2021
            }
        }

class GuitarRecommendation(BaseModel):
    """AI-generated guitar recommendation"""
    user_analysis: str = Field(..., description="Analysis of what the user is looking for")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="List of recommended guitars")
    market_insights: Optional[str] = Field(None, description="Insights about current market")
    alternative_suggestions: Optional[str] = Field(None, description="Alternative suggestions if primary recommendations don't fit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_analysis": "You're looking for a versatile electric guitar suitable for blues and rock, similar to what David Gilmour plays, within a $1000 budget.",
                "recommendations": [
                    {
                        "rank": 1,
                        "guitar_title": "Fender Stratocaster Mexican",
                        "price": 899,
                        "match_score": 0.95,
                        "why_recommended": "This is the exact model type Gilmour is famous for",
                        "pros": ["Versatile", "Great value"],
                        "cons": ["May need setup"],
                        "best_for": "Blues, rock, and Pink Floyd covers"
                    }
                ],
                "market_insights": "Current market shows good availability of Stratocasters in your price range",
                "alternative_suggestions": "Consider also looking at PRS SE models for similar versatility"
            }
        }