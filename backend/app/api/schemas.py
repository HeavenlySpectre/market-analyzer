from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AnalyzeRequest(BaseModel):
    url: str

class ProductMetadata(BaseModel):
    product_title: Optional[str] = None
    price: Optional[str] = None
    average_rating: Optional[float] = None
    total_reviews: Optional[int] = None
    shop_name: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class ChartData(BaseModel):
    rating_distribution: List[Dict[str, int]]
    positive_keywords: List[Dict[str, Any]]
    negative_keywords: List[Dict[str, Any]]

class AnalyzeResponse(BaseModel):
    message: str
    summary: str
    product_metadata: Optional[ProductMetadata] = None
    chart_data: ChartData

class ChatRequest(BaseModel):
    query: str
    product_metadata: Optional[ProductMetadata] = None

class ChatResponse(BaseModel):
    answer: str