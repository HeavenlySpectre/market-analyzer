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

class SellerReputation(BaseModel):
    seller_name: Optional[str] = None
    badges: List[str] = []
    store_rating: Optional[float] = None
    followers: Optional[int] = None
    product_count: Optional[int] = None
    chat_performance: Optional[int] = None
    on_time_shipping: Optional[int] = None
    cancellation_rate: Optional[int] = None
    join_date: Optional[str] = None
    location: Optional[str] = None
    processing_time: Optional[str] = None
    reliability_score: float = 0
    confidence_score: float = 0
    components: Dict[str, Any] = {}
    coverage_info: Dict[str, Any] = {}
    score_explanation: str = ""
    notes: List[str] = []

class ChartData(BaseModel):
    rating_distribution: List[Dict[str, int]]
    positive_keywords: List[Dict[str, Any]]
    negative_keywords: List[Dict[str, Any]]
    review_snippets: Optional[List[Dict[str, Any]]] = []
    analysis_summary: Optional[Dict[str, Any]] = None

class AnalyzeResponse(BaseModel):
    message: str
    summary: str
    product_metadata: Optional[ProductMetadata] = None
    seller_reputation: Optional[SellerReputation] = None
    chart_data: ChartData

class ChatRequest(BaseModel):
    query: str
    product_metadata: Optional[ProductMetadata] = None

class ChatResponse(BaseModel):
    answer: str