from fastapi import APIRouter, HTTPException
from .schemas import AnalyzeRequest, AnalyzeResponse, ChatRequest, ChatResponse, ChartData, ProductMetadata
from ..services import scraper_service, rag_service, analysis_service

# --- INI ADALAH BARIS YANG HILANG ATAU SALAH ---
# Mendefinisikan instance APIRouter yang akan kita gunakan
# untuk semua endpoint di file ini.
router = APIRouter()
# ----------------------------------------------------

# Endpoint sekarang harus menggunakan @router, bukan @app
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_product(request: AnalyzeRequest):
    """
    Endpoint untuk memulai analisis produk dari URL.
    """
    # Panggilan fungsi biasa (sync)
    reviews = scraper_service.scrape_product_reviews(request.url, max_reviews=40)
    
    if not reviews or "ERROR:" in reviews[0]:
        error_msg = reviews[0] if reviews else "Gagal mengambil ulasan."
        raise HTTPException(status_code=400, detail=error_msg)

    # Scrape product metadata
    metadata = scraper_service.scrape_product_metadata(request.url)
    
    index_message = rag_service.create_vector_store(reviews)
    summary = rag_service.generate_initial_summary(reviews)
    chart_data_dict = analysis_service.analyze_sentiments_and_topics(reviews)
    
    return AnalyzeResponse(
        message=f"Analisis selesai. {index_message}",
        summary=summary,
        product_metadata=ProductMetadata(**metadata),
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