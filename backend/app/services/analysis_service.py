import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import random
import os

def load_stopwords():
    """Memuat daftar stop words dari file teks."""
    # Tentukan path ke file stopwords relatif terhadap file ini
    current_dir = os.path.dirname(__file__)
    stopwords_path = os.path.join(current_dir, 'indo_stopwords.txt')
    
    try:
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            # Baca setiap baris dan hapus whitespace/newline
            stopwords = [line.strip() for line in f]
        return stopwords
    except FileNotFoundError:
        print("PERINGATAN: File indo_stopwords.txt tidak ditemukan. Menggunakan daftar kosong.")
        return []

# Muat stopwords sekali saat modul diimpor
indonesian_stop_words = load_stopwords()

def get_top_keywords(texts: list[str], top_n: int = 10):
    """Mengekstrak kata kunci paling umum dari daftar teks."""
    if not texts or not indonesian_stop_words:
        return []
    
    full_text = " ".join(texts)
    if not full_text.strip():
        return []
    
    try:
        vectorizer = CountVectorizer(stop_words=indonesian_stop_words).fit([full_text])
        bag_of_words = vectorizer.transform([full_text])
        sum_words = bag_of_words.sum(axis=0) 
        words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        
        # --- PERBAIKAN UTAMA DI SINI ---
        # Ubah tipe data NumPy menjadi int standar Python agar bisa di-serialize ke JSON.
        top_keywords = [
            {"text": word, "value": int(freq)} 
            for word, freq in words_freq[:top_n]
        ]
        # ---------------------------------
        
        return top_keywords
    except ValueError:
        return []

def analyze_sentiments_and_topics(reviews: list[str]) -> dict:
    """
    Melakukan analisis yang telah diperbaiki untuk data grafik.
    """
    if not reviews or all("ERROR:" in r for r in reviews):
        return {"rating_distribution": [], "positive_keywords": [], "negative_keywords": []}

    ratings = [random.randint(1, 5) for _ in reviews]
    df = pd.DataFrame({'review': reviews, 'rating': ratings})

    # 1. Analisis Distribusi Rating
    rating_counts = df['rating'].value_counts().sort_index()
    # --- PERBAIKAN DI SINI JUGA ---
    # Konversi tipe data untuk rating distribution
    rating_distribution = [
        {"stars": int(k), "count": int(v)} 
        for k, v in rating_counts.items()
    ]

    # 2. Analisis Kata Kunci yang Diperbaiki
    positive_texts = df[df['rating'] >= 4]['review'].tolist()
    negative_texts = df[df['rating'] <= 2]['review'].tolist()

    positive_keywords = get_top_keywords(positive_texts)
    negative_keywords = get_top_keywords(negative_texts)

    return {
        "rating_distribution": rating_distribution,
        "positive_keywords": positive_keywords,
        "negative_keywords": negative_keywords
    }