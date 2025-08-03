# main.py
import sys
import asyncio

if sys.platform.startswith('win'):
    # Force SelectorEventLoop on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import endpoints

app = FastAPI(
    title="Marketplace Analyzer API",
    description="API untuk menganalisis ulasan produk dari marketplace.",
    version="1.0.0"
)

# Konfigurasi CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sertakan router dari endpoints.py
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Selamat datang di Marketplace Analyzer API!"}