from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyzeRequest(BaseModel):
    url: str

class ChartData(BaseModel):
    rating_distribution: List[Dict[str, int]]
    positive_keywords: List[Dict[str, Any]]
    negative_keywords: List[Dict[str, Any]]

class AnalyzeResponse(BaseModel):
    message: str
    summary: str
    chart_data: ChartData

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str