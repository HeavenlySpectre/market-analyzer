from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def construct_review_url(product_url: str) -> str:
    """
    Mengubah URL produk Tokopedia menjadi URL halaman ulasannya.
    """
    cleaned_url = product_url.split('?')[0]
    if cleaned_url.endswith('/review'):
        return cleaned_url
    if cleaned_url.endswith('/'):
        return f"{cleaned_url}review"
    return f"{cleaned_url}/review"


def scrape_product_reviews(url: str) -> list[str]:
    """
    Mengambil ulasan produk menggunakan Selenium dan BeautifulSoup.
    """
    # --- UPDATE SELECTOR DI SINI ---
    # Selector ini diperbarui berdasarkan struktur Tokopedia saat ini.
    # Anda mungkin perlu menyesuaikannya lagi jika berubah.
    REVIEW_CONTAINER_SELECTOR = "section#review-feed article"
    REVIEW_TEXT_SELECTOR = "span[data-testid='lblItemUlasan']"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    reviews = []
    try:
        review_page_url = construct_review_url(url)
        print(f"[SCRAPER LOG] Mengakses halaman ulasan di: {review_page_url}")
        
        driver.get(review_page_url)
        time.sleep(3) # Tunggu sebentar agar elemen awal muncul

        # Gulir halaman beberapa kali untuk memuat semua ulasan
        for i in range(5):
            print(f"[SCRAPER LOG] Menggulir halaman... ({i+1}/5)")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        print("[SCRAPER LOG] Selesai menggulir. Mem-parsing HTML dengan BeautifulSoup...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        review_elements = soup.select(REVIEW_CONTAINER_SELECTOR)
        print(f"[SCRAPER LOG] Menemukan {len(review_elements)} elemen kontainer ulasan.")
        
        if not review_elements:
            return ["ERROR: Elemen kontainer ulasan (listAllReview) tidak ditemukan. Periksa kembali selector kontainer."]

        for element in review_elements:
            text_element = element.select_one(REVIEW_TEXT_SELECTOR)
            if text_element:
                reviews.append(text_element.get_text(strip=True))
        
        print(f"[SCRAPER LOG] Berhasil mengekstrak {len(reviews)} teks ulasan.")
        
        if not reviews:
             return ["ERROR: Kontainer ulasan ditemukan, tetapi tidak ada teks ulasan (lblReviewComment) yang berhasil diekstrak. Periksa selector teks."]

    except Exception as e:
        return [f"ERROR: Terjadi kesalahan fatal saat scraping - {type(e).__name__}: {str(e)}"]
    finally:
        driver.quit()
    
    final_reviews = [r for r in reviews if r]
    
    if not final_reviews:
        return ["ERROR: Semua ulasan yang diambil ternyata kosong setelah difilter. Mungkin ada masalah dengan ekstraksi teks."]

    print(f"[SCRAPER LOG] Scraping berhasil. Mengembalikan {len(final_reviews)} ulasan.")
    return final_reviews