from fastapi import APIRouter, HTTPException
from .schemas import AnalyzeRequest, AnalyzeResponse, ChatRequest, ChatResponse, ChartData, ProductMetadata, SellerReputation
from ..services import scraper_service, rag_service, analysis_service
from ..services.system_metrics_service import system_metrics

# --- INI ADALAH BARIS YANG HILANG ATAU SALAH ---
# Mendefinisikan instance APIRouter yang akan kita gunakan
# untuk semua endpoint di file ini.
router = APIRouter()
# ----------------------------------------------------

# Endpoint sekarang harus menggunakan @router, bukan @app
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_product(request: AnalyzeRequest):
    """
    Endpoint untuk memulai analisis produk dengan real sentiment analysis dan seller reputation.
    """
    # Use comprehensive scraping that includes seller reputation
    comprehensive_data = scraper_service.scrape_product_with_seller_reputation(request.url, max_reviews=40)
    
    reviews_data = comprehensive_data.get("reviews_data", [])
    metadata = comprehensive_data.get("metadata", {})
    seller_reputation = comprehensive_data.get("seller_reputation", {})
    
    if not reviews_data or "ERROR:" in reviews_data[0].get("text", ""):
        error_msg = reviews_data[0].get("text", "") if reviews_data else "Gagal mengambil ulasan."
        raise HTTPException(status_code=400, detail=error_msg)

    # Extract just the text for RAG (backward compatibility)
    review_texts = [review["text"] for review in reviews_data if "text" in review]
    
    index_message = rag_service.create_vector_store(review_texts)
    summary = rag_service.generate_initial_summary(review_texts)
    
    # Use new analysis function with real rating data
    chart_data_dict = analysis_service.analyze_sentiments_and_topics(reviews_data)
    
    return AnalyzeResponse(
        message=f"Analisis selesai dengan seller reputation. {index_message}",
        summary=summary,
        product_metadata=ProductMetadata(**metadata),
        seller_reputation=SellerReputation(**seller_reputation),
        chart_data=ChartData(**chart_data_dict)
    )

@router.post("/chat", response_model=ChatResponse)
def chat_with_reviews(request: ChatRequest):
    """
    Endpoint untuk mengirim pertanyaan ke RAG pipeline.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Pertanyaan tidak boleh kosong.")
    
    answer = rag_service.query_rag(request.query, request.product_metadata)
    return ChatResponse(answer=answer)

@router.get("/system-stats")
def get_system_stats():
    """
    Endpoint untuk mengambil statistik sistem real-time.
    """
    return system_metrics.get_all_metrics()