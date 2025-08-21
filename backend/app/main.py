# main.py
import sys
import asyncio
import os

if sys.platform.startswith('win'):
    # Force SelectorEventLoop on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import endpoints
from .middleware.metrics_middleware import MetricsMiddleware

app = FastAPI(
    title="Marketplace Analyzer API",
    description="API untuk menganalisis ulasan produk dari marketplace.",
    version="1.0.0"
)

# Konfigurasi CORS (Cross-Origin Resource Sharing) - env driven
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
origins = [origin.strip() for origin in cors_origins_env.split(",")]

# Add metrics middleware first (before CORS)
app.add_middleware(MetricsMiddleware)

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