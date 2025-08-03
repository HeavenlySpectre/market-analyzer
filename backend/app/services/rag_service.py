import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ..core.config import settings

# --- KONFIGURASI YANG BENAR ---

# 1. Konfigurasi GLOBAL untuk pustaka google-generativeai asli
# Ini akan digunakan oleh genai.GenerativeModel
genai.configure(api_key=settings.GEMINI_API_KEY)

# 2. Inisialisasi model LLM untuk generasi teks
# Ia sekarang akan secara otomatis menggunakan kunci dari genai.configure()
# Kita HAPUS argumen api_key dari sini.
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Inisialisasi model Embedding dari LangChain
# Pembungkus LangChain ini MEMBUTUHKAN api key secara langsung.
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    google_api_key=settings.GEMINI_API_KEY
)
# ---------------------------------

vector_store = None

def create_vector_store(texts: list[str]):
    global vector_store
    if not texts:
        return "Tidak ada teks ulasan untuk diindeks."

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.create_documents(texts)
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model
    )
    return f"Berhasil mengindeks {len(texts)} ulasan menjadi {len(chunks)} potongan."

def generate_initial_summary(reviews: list[str]) -> str:
    sample_reviews = " ".join(reviews[:20])
    prompt = f"""
    Anda adalah seorang analis produk yang ahli. Berdasarkan ulasan berikut, buatlah ringkasan singkat dalam 2-3 poin utama mengenai kelebihan dan 2-3 poin utama mengenai kekurangan produk ini.
    Gunakan format:
    **Kelebihan:**
    - Poin 1
    - Poin 2
    
    **Kekurangan:**
    - Poin 1
    - Poin 2

    Ulasan:
    ---
    {sample_reviews}
    ---
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gagal membuat ringkasan: {str(e)}"

def query_rag(user_query: str, product_metadata=None) -> str:
    global vector_store
    if vector_store is None:
        return "Database ulasan belum dibuat. Lakukan analisis terlebih dahulu."

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    relevant_docs = retriever.invoke(user_query)  # Updated to use invoke instead of deprecated method
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

    # Add product metadata to context if available
    product_info = ""
    if product_metadata:
        product_info = f"""
Informasi Produk:
- Nama: {product_metadata.product_title or 'Tidak tersedia'}
- Harga: {product_metadata.price or 'Tidak tersedia'}
- Rating: {product_metadata.average_rating or 'Tidak tersedia'}/5
- Total Ulasan: {product_metadata.total_reviews or 'Tidak tersedia'}
- Toko: {product_metadata.shop_name or 'Tidak tersedia'}
- Kategori: {product_metadata.category or 'Tidak tersedia'}
- Deskripsi: {product_metadata.description or 'Tidak tersedia'}

"""

    prompt = f"""
    Anda adalah asisten AI yang menjawab pertanyaan berdasarkan informasi produk dan ulasan pelanggan. Gunakan semua informasi yang tersedia untuk memberikan jawaban yang lengkap dan akurat.

    {product_info}
    Konteks Ulasan Pelanggan:
    ---
    {context_text}
    ---

    Pertanyaan Pengguna: {user_query}

    Jawaban Komprehensif Berdasarkan Informasi Produk dan Ulasan:
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gagal mendapatkan jawaban dari AI: {str(e)}"