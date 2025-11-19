"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (retain for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Historical event schemas for the app
class SubtitleCue(BaseModel):
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")
    text: str = Field(..., description="Subtitle text")

class Event(BaseModel):
    """
    Paris historical events
    Collection name: "event"
    """
    title: str
    year: int = Field(..., description="Year of the event (negative for BCE)")
    date: Optional[str] = Field(None, description="Optional date string, e.g., '1789-07-14'")
    description: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    images: List[str] = Field(default_factory=list, description="Image URLs")
    audio_url: Optional[str] = Field(None, description="Narration audio URL (mp3)")
    subtitles: List[SubtitleCue] = Field(default_factory=list, description="Timed subtitles")
