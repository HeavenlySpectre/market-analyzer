import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
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

def analyze_sentiment_heuristic(text: str) -> int:
    """
    Melakukan analisis sentimen sederhana berdasarkan kata kunci positif/negatif.
    Returns rating 1-5 based on sentiment.
    """
    text = text.lower()
    
    # Indonesian positive keywords
    positive_keywords = [
        'bagus', 'baik', 'mantap', 'keren', 'suka', 'puas', 'senang', 'cocok', 
        'recommended', 'bagus', 'oke', 'wangi', 'enak', 'murah', 'cepat', 
        'sesuai', 'ori', 'original', 'berkualitas', 'worth', 'love', 'perfect',
        'excellent', 'amazing', 'fantastic', 'great', 'good', 'best', 'nice'
    ]
    
    # Indonesian negative keywords  
    negative_keywords = [
        'jelek', 'buruk', 'kecewa', 'tidak', 'gak', 'ngga', 'bau', 'rusak',
        'palsu', 'fake', 'lambat', 'lama', 'mahal', 'zonk', 'mengecewakan',
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'disappointing'
    ]
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_keywords if word in text)
    negative_count = sum(1 for word in negative_keywords if word in text)
    
    # Simple heuristic mapping to 1-5 stars
    net_sentiment = positive_count - negative_count
    
    if net_sentiment >= 3:
        return 5  # Very positive
    elif net_sentiment >= 1:
        return 4  # Positive  
    elif net_sentiment == 0:
        return 3  # Neutral
    elif net_sentiment >= -2:
        return 2  # Negative
    else:
        return 1  # Very negative

def get_top_keywords(texts: list[str], top_n: int = 10, label_suffix: str = ""):
    """Mengekstrak kata kunci paling umum dari daftar teks dengan fallback untuk stopwords."""
    if not texts:
        return []
    
    full_text = " ".join(texts)
    if not full_text.strip():
        return []
    
    try:
        # Use stopwords if available, otherwise use basic filtering
        if indonesian_stop_words:
            vectorizer = CountVectorizer(stop_words=indonesian_stop_words).fit([full_text])
            label = f"top keywords{label_suffix}"
        else:
            # Fallback: basic filtering of very common words
            basic_stopwords = ['dan', 'yang', 'di', 'untuk', 'dengan', 'ini', 'itu', 'tidak', 'ke', 'dari', 'pada', 'adalah', 'atau', 'juga', 'akan', 'sudah', 'ada', 'bisa', 'saya', 'kita', 'mereka']
            vectorizer = CountVectorizer(stop_words=basic_stopwords, min_df=1, max_df=0.8).fit([full_text])
            label = f"raw terms{label_suffix}"
            
        bag_of_words = vectorizer.transform([full_text])
        sum_words = bag_of_words.sum(axis=0) 
        words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        
        # Convert numpy types to standard Python int for JSON serialization
        top_keywords = [
            {"text": word, "value": int(freq), "label": label} 
            for word, freq in words_freq[:top_n]
        ]
        
        return top_keywords
    except ValueError:
        return []

def analyze_sentiments_and_topics(reviews_data: list[dict]) -> dict:
    """
    Melakukan analisis REAL berdasarkan data aktual dari scraping.
    Menggunakan rating asli dari halaman atau sentiment analysis sebagai fallback.
    """
    if not reviews_data or all("ERROR:" in r.get("text", "") for r in reviews_data):
        return {
            "rating_distribution": [], 
            "positive_keywords": [], 
            "negative_keywords": [],
            "review_snippets": [],
            "analysis_summary": "No valid reviews found"
        }

    # Process ratings: use actual ratings or sentiment analysis
    processed_reviews = []
    ratings_from_page = 0
    ratings_from_sentiment = 0
    
    for review_data in reviews_data:
        text = review_data.get("text", "")
        original_rating = review_data.get("rating")
        
        if original_rating and 1 <= original_rating <= 5:
            # Use actual rating from page
            rating = original_rating
            ratings_from_page += 1
            source = "page"
        else:
            # Use sentiment analysis as fallback
            rating = analyze_sentiment_heuristic(text)
            ratings_from_sentiment += 1
            source = "sentiment"
            
        processed_reviews.append({
            "text": text,
            "rating": rating,
            "source": source
        })
    
    # Create DataFrame for analysis
    df = pd.DataFrame(processed_reviews)
    
    # 1. Real Rating Distribution Analysis
    rating_counts = df['rating'].value_counts().sort_index()
    rating_distribution = [
        {"stars": int(k), "count": int(v)} 
        for k, v in rating_counts.items()
    ]

    # 2. Enhanced Keyword Analysis with fallback - limit to top 5
    positive_texts = df[df['rating'] >= 4]['text'].tolist()
    negative_texts = df[df['rating'] <= 2]['text'].tolist()

    positive_keywords = get_top_keywords(positive_texts, top_n=5, label_suffix=" (positive reviews)")
    negative_keywords = get_top_keywords(negative_texts, top_n=5, label_suffix=" (negative reviews)")

    # 3. Review Snippets for Explainability
    review_snippets = []
    
    # Get examples for each rating
    for stars in [5, 4, 3, 2, 1]:
        matching_reviews = df[df['rating'] == stars]['text'].tolist()
        if matching_reviews:
            # Take first review as example, truncate if too long
            snippet = matching_reviews[0]
            if len(snippet) > 150:
                snippet = snippet[:147] + "..."
            review_snippets.append({
                "stars": stars,
                "text": snippet,
                "count": len(matching_reviews)
            })
    
    # 4. Analysis Summary
    total_reviews = len(processed_reviews)
    avg_rating = df['rating'].mean() if total_reviews > 0 else 0
    
    analysis_summary = {
        "total_reviews": total_reviews,
        "average_rating": round(avg_rating, 2),
        "ratings_from_page": ratings_from_page,
        "ratings_from_sentiment": ratings_from_sentiment,
        "data_quality": "high" if ratings_from_page > ratings_from_sentiment else "medium"
    }

    return {
        "rating_distribution": rating_distribution,
        "positive_keywords": positive_keywords,
        "negative_keywords": negative_keywords,
        "review_snippets": review_snippets,
        "analysis_summary": analysis_summary
    }