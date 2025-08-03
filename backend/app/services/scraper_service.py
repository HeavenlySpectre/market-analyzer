from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re

def scrape_product_metadata(url: str) -> dict:
    """
    Mengambil metadata produk (nama, harga, rating, dll) dari halaman produk Tokopedia.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    metadata = {
        "title": "",
        "price": "",
        "description": "",
        "category": "",
        "average_rating": 0.0,
        "total_reviews": 0,
        "shop_name": "",
        "image_url": ""
    }

    try:
        print(f"[METADATA SCRAPER] Mengakses halaman produk: {url}")
        driver.get(url)
        time.sleep(3)  # Wait for page to load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Scrape product title
        title_selectors = [
            'h1[data-testid="lblPDPDetailProductName"]',
            'h1.css-1os9jjn',
            '.prd_link-product-name',
            'h1'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                metadata["title"] = title_element.get_text(strip=True)
                break
        
        # Scrape price
        price_selectors = [
            '[data-testid="lblPDPDetailProductPrice"]',
            '.price',
            '.css-1ksb19c',
            '.prd_link-prod-price'
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                metadata["price"] = price_element.get_text(strip=True)
                break
        
        # Scrape rating
        rating_selectors = [
            '[data-testid="lblPDPDetailProductRatingNumber"]',
            '.prd_rating-average-text',
            '.css-153qjw7'
        ]
        
        for selector in rating_selectors:
            rating_element = soup.select_one(selector)
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                try:
                    # Extract numeric rating
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        metadata["average_rating"] = float(rating_match.group(1))
                except (ValueError, AttributeError):
                    pass
                break
        
        # Scrape total reviews
        review_count_selectors = [
            '[data-testid="lblPDPDetailProductRatingCounter"]',
            '.prd_rating-review-count',
            '.css-1duhs3e'
        ]
        
        for selector in review_count_selectors:
            review_element = soup.select_one(selector)
            if review_element:
                review_text = review_element.get_text(strip=True)
                try:
                    # Extract numeric count (handle "1.2k" format)
                    review_match = re.search(r'(\d+\.?\d*)\s*([kK]?)', review_text)
                    if review_match:
                        count = float(review_match.group(1))
                        if review_match.group(2).lower() == 'k':
                            count *= 1000
                        metadata["total_reviews"] = int(count)
                except (ValueError, AttributeError):
                    pass
                break
        
        # Scrape shop name
        shop_selectors = [
            '[data-testid="lblPDPDetailMerchantName"]',
            '.shop-name',
            '.css-1kr2wmi'
        ]
        
        for selector in shop_selectors:
            shop_element = soup.select_one(selector)
            if shop_element:
                metadata["shop_name"] = shop_element.get_text(strip=True)
                break
        
        # Scrape product image
        image_selectors = [
            'img[data-testid="PDPImageMain"]',
            '.css-1c345mg img',
            '.prd_media-content img'
        ]
        
        for selector in image_selectors:
            image_element = soup.select_one(selector)
            if image_element and image_element.get('src'):
                metadata["image_url"] = image_element.get('src')
                break
        
        # Scrape description (simplified)
        desc_selectors = [
            '[data-testid="lblPDPDescriptionProduk"]',
            '.css-1k1relq',
            '.prd_desc-content'
        ]
        
        for selector in desc_selectors:
            desc_element = soup.select_one(selector)
            if desc_element:
                desc_text = desc_element.get_text(strip=True)
                # Limit description to first 200 characters
                metadata["description"] = desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
                break
        
        # Try to get category from breadcrumb
        breadcrumb_selectors = [
            '[data-testid="lblPDPCrumb"]',
            '.css-l5njp4',
            '.breadcrumb'
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb = soup.select_one(selector)
            if breadcrumb:
                breadcrumb_text = breadcrumb.get_text(strip=True)
                # Take the last meaningful part as category
                parts = breadcrumb_text.split('>')
                if len(parts) >= 2:
                    metadata["category"] = parts[-2].strip()
                break
        
        print(f"[METADATA SCRAPER] Successfully scraped metadata for: {metadata.get('title', 'Unknown Product')}")
        
    except Exception as e:
        print(f"[METADATA SCRAPER] Error: {str(e)}")
        
    finally:
        driver.quit()
    
    return metadata

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


def scrape_product_reviews(url: str, max_reviews: int = 50) -> list[str]:
    """
    Mengambil ulasan produk menggunakan Selenium dan BeautifulSoup.
    Akan mencoba mengambil maksimal max_reviews ulasan dengan pagination.
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

        page_number = 1
        max_pages = 10  # Limit to prevent infinite loops
        
        while len(reviews) < max_reviews and page_number <= max_pages:
            print(f"[SCRAPER LOG] Processing page {page_number}... Current reviews: {len(reviews)}")
            
            # Wait for page to load and scroll to show all reviews on current page
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Parse current page content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_elements = soup.select(REVIEW_CONTAINER_SELECTOR)
            
            print(f"[SCRAPER LOG] Found {len(review_elements)} review elements on page {page_number}")
            
            # Extract reviews from current page
            page_reviews = []
            for element in review_elements:
                text_element = element.select_one(REVIEW_TEXT_SELECTOR)
                if text_element:
                    review_text = text_element.get_text(strip=True)
                    if review_text and review_text not in reviews:  # Avoid duplicates
                        page_reviews.append(review_text)
                        reviews.append(review_text)
            
            print(f"[SCRAPER LOG] Extracted {len(page_reviews)} new reviews from page {page_number}, total: {len(reviews)}")
            
            # If we have enough reviews, break
            if len(reviews) >= max_reviews:
                print(f"[SCRAPER LOG] Reached target of {max_reviews} reviews, stopping...")
                break
            
            # Try to find and click next page button
            try:
                # Look for pagination buttons
                pagination_buttons = driver.find_elements("css selector", "button[data-unf='pagination-item']")
                next_button = None
                
                # Find the next button (not disabled, not current page)
                for button in pagination_buttons:
                    if (not button.get_attribute("disabled") and 
                        button.get_attribute("data-active") != "true" and
                        button.text.isdigit() and
                        int(button.text) == page_number + 1):
                        next_button = button
                        break
                
                # If no specific next page number found, try generic next button
                if not next_button:
                    try:
                        next_button = driver.find_element("css selector", "button[aria-label*='selanjutnya']")
                    except Exception:
                        pass
                
                if next_button:
                    print("[SCRAPER LOG] Clicking next page button...")
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)  # Wait for new page to load
                    page_number += 1
                else:
                    print("[SCRAPER LOG] No more pages available, stopping pagination...")
                    break
                    
            except Exception as e:
                print(f"[SCRAPER LOG] Error navigating to next page: {str(e)}")
                break
        
        print(f"[SCRAPER LOG] Pagination complete. Processed {page_number} pages.")
        
        # Remove any duplicate reviews that might have slipped through
        final_reviews = []
        for review in reviews:
            if review not in final_reviews:
                final_reviews.append(review)
        
        print(f"[SCRAPER LOG] Final deduplication: {len(reviews)} -> {len(final_reviews)} unique reviews")
        
        if not final_reviews:
            return ["ERROR: Tidak ada ulasan yang berhasil diekstrak dari semua halaman."]

    except Exception as e:
        return [f"ERROR: Terjadi kesalahan fatal saat scraping - {type(e).__name__}: {str(e)}"]
    finally:
        driver.quit()
    
    # Limit to max_reviews if we got more than needed
    if len(final_reviews) > max_reviews:
        final_reviews = final_reviews[:max_reviews]

    print(f"[SCRAPER LOG] Scraping berhasil. Mengembalikan {len(final_reviews)} ulasan.")
    return final_reviews