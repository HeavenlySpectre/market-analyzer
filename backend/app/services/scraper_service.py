from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import logging
from urllib.parse import urlparse
from .seller_reputation_service import analyze_seller_reputation

# Configure logging for scraper
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Domain allowlist for scraping
ALLOWED_DOMAINS = ['tokopedia.com', 'www.tokopedia.com']

def validate_url(url: str) -> bool:
    """
    Validate that URL belongs to allowed domains (Tokopedia only).
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        is_valid = any(domain == allowed or domain.endswith('.' + allowed) for allowed in ALLOWED_DOMAINS)
        if not is_valid:
            logger.warning(f"Domain not allowed: {domain}. Only Tokopedia URLs are supported.")
        return is_valid
    except Exception as e:
        logger.error(f"Error parsing URL {url}: {str(e)}")
        return False

def scrape_product_metadata(url: str) -> dict:
    """
    Mengambil metadata produk (nama, harga, rating, dll) dari halaman produk Tokopedia.
    Includes domain validation and explicit waits for better reliability.
    """
    # Validate domain first
    if not validate_url(url):
        return {
            "product_title": "ERROR: URL tidak valid atau domain tidak didukung",
            "price": "",
            "description": "",
            "category": "",
            "average_rating": 0.0,
            "total_reviews": 0,
            "shop_name": "",
            "image_url": ""
        }

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)  # 15 second timeout for explicit waits
    
    metadata = {
        "product_title": "",
        "price": "",
        "description": "",
        "category": "",
        "average_rating": 0.0,
        "total_reviews": 0,
        "shop_name": "",
        "image_url": ""
    }

    try:
        logger.info(f"[METADATA] Accessing product page: {url}")
        driver.get(url)
        
        # Wait for main product container to load
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-testid="lblPDPDetailProductName"], h1')))
            logger.info("[METADATA] Product page loaded successfully")
        except TimeoutException:
            logger.warning("[METADATA] Timeout waiting for product page to load")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Scrape product title with priority on stable selectors
        title_selectors = [
            'h1[data-testid="lblPDPDetailProductName"]',  # Most stable
            'h1.css-1os9jjn',
            '.prd_link-product-name',
            'h1'  # Fallback
        ]
        
        for i, selector in enumerate(title_selectors):
            title_element = soup.select_one(selector)
            if title_element:
                metadata["product_title"] = title_element.get_text(strip=True)
                logger.info(f"[METADATA] Title found using selector {i+1}: {metadata['product_title'][:50]}...")
                break
        
        # Scrape price with stable selectors
        price_selectors = [
            '[data-testid="lblPDPDetailProductPrice"]',  # Most stable
            '.price',
            '.css-1ksb19c',
            '.prd_link-prod-price'
        ]
        
        for i, selector in enumerate(price_selectors):
            price_element = soup.select_one(selector)
            if price_element:
                metadata["price"] = price_element.get_text(strip=True)
                logger.info(f"[METADATA] Price found using selector {i+1}: {metadata['price']}")
                break
        
        # Scrape rating with stable selectors - Enhanced with more patterns
        rating_selectors = [
            '[data-testid="lblPDPDetailProductRatingNumber"]',  # Most stable
            '[data-testid="lblPDPDetailProductRatingCounter"]',  # This contains "(3.554 rating)"
            '.prd_rating-average-text',
            '.css-153qjw7',
            '*[class*="rating"]',  # Any element with "rating" in class name
        ]
        
        for i, selector in enumerate(rating_selectors):
            rating_element = soup.select_one(selector)
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                logger.info(f"[METADATA] Rating element {i+1} text: '{rating_text}'")  # Debug log
                try:
                    # Extract numeric rating - handle formats like "(3.554 rating)" or "4.5"
                    rating_match = re.search(r'(\d+\.\d+)', rating_text)  # Look for decimal numbers like 3.554
                    if rating_match:
                        metadata["average_rating"] = float(rating_match.group(1))
                        logger.info(f"[METADATA] Rating found using selector {i+1}: {metadata['average_rating']}")
                        break
                    else:
                        # Fallback to any number at start of text
                        rating_match = re.search(r'^(\d+)', rating_text)
                        if rating_match:
                            rating_value = float(rating_match.group(1))
                            # Only accept if it's a reasonable rating (1-5 range)
                            if 1 <= rating_value <= 5:
                                metadata["average_rating"] = rating_value
                                logger.info(f"[METADATA] Rating found using selector {i+1}: {metadata['average_rating']}")
                                break
                except (ValueError, AttributeError):
                    logger.warning(f"[METADATA] Could not parse rating from: {rating_text}")
        
        # If no rating found from selectors, search more broadly
        if "average_rating" not in metadata:
            logger.info("[METADATA] Searching for rating in broader patterns...")
            # Look for rating patterns in the overall page content
            page_text = soup.get_text()
            rating_patterns = [
                r'(\d+\.\d+)\s*(?:bintang|star|rating)',  # "4.5 bintang" or "4.5 rating"
                r'rating[:\s]*(\d+\.\d+)',               # "rating: 4.5"
                r'(\d+\.\d+)\s*/\s*5',                   # "4.5 / 5"
            ]
            
            for pattern in rating_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        rating_value = float(match.group(1))
                        if 1 <= rating_value <= 5:
                            metadata["average_rating"] = rating_value
                            logger.info(f"[METADATA] Rating found from text pattern: {rating_value}")
                            break
                    except (ValueError, IndexError):
                        continue
        
        # Scrape total reviews - Look for specific patterns like "2243 ulasan"
        logger.info("[METADATA] Searching for review count...")
        
        # Search for elements containing the pattern "number ulasan"
        all_elements = soup.find_all(['span', 'div', 'p', 'a'])
        
        for element in all_elements:
            text = element.get_text(strip=True)
            
            # Look specifically for "number ulasan" pattern (e.g., "2243 ulasan")
            ulasan_match = re.search(r'(\d+)\s+ulasan', text, re.IGNORECASE)
            if ulasan_match:
                try:
                    metadata["total_reviews"] = int(ulasan_match.group(1))
                    logger.info(f"[METADATA] Review count found: {metadata['total_reviews']} (from pattern 'number ulasan')")
                    break
                except ValueError:
                    continue
        
        # If not found, try "number rating • number ulasan" pattern  
        if "total_reviews" not in metadata:
            for element in all_elements:
                text = element.get_text(strip=True)
                
                # Look for "3554 rating • 2243 ulasan" pattern
                rating_ulasan_match = re.search(r'(\d+)\s+rating\s*•\s*(\d+)\s+ulasan', text, re.IGNORECASE)
                if rating_ulasan_match:
                    try:
                        metadata["total_reviews"] = int(rating_ulasan_match.group(2))  # Take the second number (ulasan count)
                        logger.info(f"[METADATA] Review count found: {metadata['total_reviews']} (from pattern 'rating • ulasan')")
                        break
                    except ValueError:
                        continue
        
        # Final fallback: look for standalone numbers near "ulasan"
        if "total_reviews" not in metadata:
            logger.info("[METADATA] Trying fallback search for review count...")
            for element in all_elements:
                text = element.get_text(strip=True).lower()
                if 'ulasan' in text:
                    # Find all numbers in this text
                    numbers = re.findall(r'\b(\d+)\b', text)
                    for num in numbers:
                        try:
                            # Skip very small numbers (likely percentages) and very large numbers (likely not review counts)
                            num_val = int(num)
                            if 10 <= num_val <= 999999:  # Reasonable range for review counts
                                metadata["total_reviews"] = num_val
                                logger.info(f"[METADATA] Review count found via fallback: {metadata['total_reviews']}")
                                break
                        except ValueError:
                            continue
                    if "total_reviews" in metadata:
                        break
        
        # Scrape shop name with stable selectors
        shop_selectors = [
            '[data-testid="lblPDPDetailMerchantName"]',  # Most stable
            '.shop-name',
            '.css-1kr2wmi'
        ]
        
        for i, selector in enumerate(shop_selectors):
            shop_element = soup.select_one(selector)
            if shop_element:
                metadata["shop_name"] = shop_element.get_text(strip=True)
                logger.info(f"[METADATA] Shop name found using selector {i+1}: {metadata['shop_name']}")
                break
        
        # Scrape product image with stable selectors
        image_selectors = [
            'img[data-testid="PDPImageMain"]',  # Most stable
            '.css-1c345mg img',
            '.prd_media-content img'
        ]
        
        for i, selector in enumerate(image_selectors):
            image_element = soup.select_one(selector)
            if image_element and image_element.get('src'):
                metadata["image_url"] = image_element.get('src')
                logger.info(f"[METADATA] Image found using selector {i+1}")
                break
        
        # Scrape description with stable selectors
        desc_selectors = [
            '[data-testid="lblPDPDescriptionProduk"]',  # Most stable
            '.css-1k1relq',
            '.prd_desc-content'
        ]
        
        # Try to expand description first by clicking "See More" button if it exists
        try:
            see_more_selectors = [
                'button[data-testid="btnPDPSeeMore"]',
                'button:contains("Lihat Selengkapnya")',
                'button:contains("Selengkapnya")',
                '.css-1nv6gtb'
            ]
            
            for see_more_selector in see_more_selectors:
                try:
                    if see_more_selector.startswith('button:contains'):
                        # Find button by text content
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            if any(text in button.text for text in ["Lihat Selengkapnya", "Selengkapnya", "See More"]):
                                driver.execute_script("arguments[0].click();", button)
                                logger.info("[METADATA] Clicked 'See More' button to expand description")
                                time.sleep(1)  # Wait for expansion
                                break
                    else:
                        see_more_btn = driver.find_element(By.CSS_SELECTOR, see_more_selector)
                        if see_more_btn:
                            driver.execute_script("arguments[0].click();", see_more_btn)
                            logger.info(f"[METADATA] Clicked 'See More' button using selector: {see_more_selector}")
                            time.sleep(1)  # Wait for expansion
                            break
                except Exception:
                    continue
        except Exception as e:
            logger.info(f"[METADATA] No 'See More' button found or couldn't click: {str(e)}")
        
        # Re-get the page source after potential expansion
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for i, selector in enumerate(desc_selectors):
            desc_element = soup.select_one(selector)
            if desc_element:
                # Debug: Log the raw HTML to see what we're getting
                logger.info(f"[METADATA] Raw description HTML length: {len(str(desc_element))}")
                
                # Replace <br> tags with spaces before extracting text
                for br in desc_element.find_all('br'):
                    br.replace_with(' ')
                
                desc_text = desc_element.get_text(strip=True)
                # Clean up the text - replace multiple whitespaces and line breaks with single spaces
                desc_text = re.sub(r'\s+', ' ', desc_text)
                
                # Debug: Log first and last 100 characters to verify we got the full text
                logger.info(f"[METADATA] Description start: '{desc_text[:100]}...'")
                logger.info(f"[METADATA] Description end: '...{desc_text[-100:]}'")
                
                # Remove the character limit - capture the full description
                metadata["description"] = desc_text
                logger.info(f"[METADATA] Description found using selector {i+1}: {len(desc_text)} chars")
                break
        
        # Try to get category from breadcrumb with stable selectors
        breadcrumb_selectors = [
            '[data-testid="lblPDPCrumb"]',  # Most stable
            '.css-l5njp4',
            '.breadcrumb'
        ]
        
        for i, selector in enumerate(breadcrumb_selectors):
            breadcrumb = soup.select_one(selector)
            if breadcrumb:
                breadcrumb_text = breadcrumb.get_text(strip=True)
                # Take the last meaningful part as category
                parts = breadcrumb_text.split('>')
                if len(parts) >= 2:
                    metadata["category"] = parts[-2].strip()
                    logger.info(f"[METADATA] Category found using selector {i+1}: {metadata['category']}")
                break
        
        logger.info(f"[METADATA] Successfully scraped metadata for: {metadata.get('product_title', 'Unknown Product')}")
        
    except Exception as e:
        logger.error(f"[METADATA] Error during scraping: {str(e)}")
        metadata["product_title"] = f"ERROR: {str(e)}"
        
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


def scrape_product_reviews(url: str, max_reviews: int = 50) -> list[dict]:
    """
    Mengambil ulasan produk dengan pagination, explicit waits, dan bounded retry logic.
    Returns list of review data with ratings and text for real sentiment analysis.
    """
    # Validate domain first
    if not validate_url(url):
        return ["ERROR: URL tidak valid atau domain tidak didukung. Hanya URL Tokopedia yang diperbolehkan."]
    
    # Stable selectors with data-testid priority - enhanced to extract ratings
    REVIEW_CONTAINER_SELECTOR = "section#review-feed article"  # This worked in old version
    REVIEW_TEXT_SELECTOR = "span[data-testid='lblItemUlasan']"  # This worked in old version  
    REVIEW_RATING_SELECTORS = [
        "div[data-testid='icnStarRating']",  # Star rating container
        ".shopee-rating",  # Fallback rating selector
        "[class*='star']",  # Any element with 'star' in class name
    ]
    PAGINATION_BUTTON_SELECTOR = "button[data-unf='pagination-item']"  # This worked in old version

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)  # 15 second timeout

    reviews = []
    try:
        review_page_url = construct_review_url(url)
        logger.info(f"[REVIEWS] Starting review scraping for: {review_page_url}")
        
        driver.get(review_page_url)
        
        # Wait for initial review container to load
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, REVIEW_CONTAINER_SELECTOR)))
            logger.info("[REVIEWS] Review page loaded successfully")
        except TimeoutException:
            logger.warning("[REVIEWS] Timeout waiting for review container")
            return ["ERROR: Halaman ulasan tidak dapat dimuat dalam waktu yang ditentukan."]

        page_number = 1
        max_pages = 8  # Bounded pagination to prevent infinite loops
        consecutive_empty_pages = 0  # Track empty pages for early termination
        max_consecutive_empty = 2   # Stop after 2 consecutive empty pages
        
        while len(reviews) < max_reviews and page_number <= max_pages and consecutive_empty_pages < max_consecutive_empty:
            logger.info(f"[REVIEWS] Processing page {page_number}/{max_pages} (target: {max_reviews} reviews, current: {len(reviews)})")
            
            # Wait for review content to stabilize on current page
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, REVIEW_CONTAINER_SELECTOR)))
                # Small wait for dynamic content
                time.sleep(2)
            except TimeoutException:
                logger.warning(f"[REVIEWS] Page {page_number}: Review container not found, trying to continue...")
            
            # Scroll to ensure all reviews are loaded on current page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Parse current page content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_elements = soup.select(REVIEW_CONTAINER_SELECTOR)
            
            logger.info(f"[REVIEWS] Page {page_number}: Found {len(review_elements)} review elements")
            
            # Extract reviews from current page with ratings
            page_reviews = []
            for element in review_elements:
                # Extract review text
                text_element = element.select_one(REVIEW_TEXT_SELECTOR)
                review_text = ""
                if text_element:
                    review_text = text_element.get_text(strip=True)
                
                if not review_text:
                    continue
                
                # Extract star rating from the review
                rating = None
                
                # Try different rating selectors
                for rating_selector in REVIEW_RATING_SELECTORS:
                    rating_element = element.select_one(rating_selector)
                    if rating_element:
                        # Look for filled/active star indicators
                        filled_stars = rating_element.select('[class*="filled"], [class*="active"], [style*="fill"]')
                        if filled_stars:
                            rating = len(filled_stars)
                            logger.info(f"[REVIEWS] Found {rating} star rating using selector: {rating_selector}")
                            break
                        
                        # Try to extract from data attributes
                        rating_value = rating_element.get('data-rating') or rating_element.get('data-value')
                        if rating_value:
                            try:
                                rating = int(float(rating_value))
                                logger.info(f"[REVIEWS] Found rating {rating} from data attribute")
                                break
                            except (ValueError, TypeError):
                                continue
                
                # If no rating found, try parsing from text patterns
                if rating is None:
                    # Look for rating patterns in nearby text
                    parent_text = element.get_text()
                    rating_patterns = [
                        r'(\d)\s*(?:star|bintang)',  # "5 star" or "5 bintang"
                        r'rating[:\s]*(\d)',         # "rating: 5"
                        r'(\d)/5',                   # "5/5"
                    ]
                    
                    for pattern in rating_patterns:
                        match = re.search(pattern, parent_text, re.IGNORECASE)
                        if match:
                            try:
                                rating = int(match.group(1))
                                if 1 <= rating <= 5:
                                    logger.info(f"[REVIEWS] Extracted rating {rating} from text pattern")
                                    break
                            except (ValueError, IndexError):
                                continue
                
                # Create review data object
                review_data = {
                    "text": review_text,
                    "rating": rating,
                    "has_rating": rating is not None
                }
                
                # Check for duplicates based on text
                if not any(existing["text"] == review_text for existing in reviews):
                    page_reviews.append(review_data)
                    reviews.append(review_data)
            
            reviews_found_this_page = len(page_reviews)
            logger.info(f"[REVIEWS] Page {page_number}: Extracted {reviews_found_this_page} new unique reviews (total: {len(reviews)})")
            
            # Track consecutive empty pages
            if reviews_found_this_page == 0:
                consecutive_empty_pages += 1
                logger.warning(f"[REVIEWS] Page {page_number}: No new reviews found ({consecutive_empty_pages}/{max_consecutive_empty} consecutive empty)")
            else:
                consecutive_empty_pages = 0  # Reset counter
            
            # Check if we have enough reviews
            if len(reviews) >= max_reviews:
                logger.info(f"[REVIEWS] Target reached: {len(reviews)}/{max_reviews} reviews collected")
                break
            
            # Try to navigate to next page with retry logic
            next_page_found = False
            for attempt in range(2):  # Bounded retry for pagination
                try:
                    # Look for pagination buttons - use the same approach as the old version
                    pagination_buttons = driver.find_elements(By.CSS_SELECTOR, PAGINATION_BUTTON_SELECTOR)
                    next_button = None
                    
                    # Find the next page button (not disabled, not current page)
                    for button in pagination_buttons:
                        if (not button.get_attribute("disabled") and 
                            button.get_attribute("data-active") != "true" and
                            button.text.isdigit() and
                            int(button.text) == page_number + 1):
                            next_button = button
                            break
                    
                    # Fallback to generic next button - simplified approach
                    if not next_button:
                        try:
                            next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='selanjutnya']")
                        except Exception:
                            pass
                    
                    if next_button:
                        logger.info(f"[REVIEWS] Page {page_number}: Clicking next page button (attempt {attempt + 1})")
                        # Use the old working approach - scroll and click
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)  # Use same timing as old version
                        
                        # Simple success check - if we can find pagination again, we navigated
                        try:
                            # Wait a bit and check if page changed
                            time.sleep(2)
                            new_pagination = driver.find_elements(By.CSS_SELECTOR, PAGINATION_BUTTON_SELECTOR)
                            if new_pagination:  # If we still have pagination, assume success
                                next_page_found = True
                                page_number += 1
                                break
                        except Exception:
                            logger.warning(f"[REVIEWS] Could not verify page navigation on attempt {attempt + 1}")
                            if attempt == 0:  # Retry once
                                time.sleep(2)
                                continue
                    else:
                        logger.info(f"[REVIEWS] Page {page_number}: No next page button found")
                        break
                        
                except Exception as e:
                    logger.warning(f"[REVIEWS] Page navigation error on attempt {attempt + 1}: {str(e)}")
                    if attempt == 0:  # Retry once
                        time.sleep(2)
                        continue
                    break
            
            if not next_page_found:
                logger.info(f"[REVIEWS] No more pages available after page {page_number}")
                break
        
        # Final summary
        total_pages_processed = page_number
        logger.info(f"[REVIEWS] Scraping completed: {len(reviews)} reviews from {total_pages_processed} pages")
        
        # Remove any duplicate reviews that might have slipped through
        unique_reviews = []
        seen_texts = set()
        for review in reviews:
            if review["text"] not in seen_texts:
                unique_reviews.append(review)
                seen_texts.add(review["text"])
        
        if len(unique_reviews) != len(reviews):
            logger.info(f"[REVIEWS] Deduplication: {len(reviews)} -> {len(unique_reviews)} unique reviews")
        
        # Count how many reviews have ratings
        reviews_with_ratings = sum(1 for r in unique_reviews if r["has_rating"])
        logger.info(f"[REVIEWS] Ratings found: {reviews_with_ratings}/{len(unique_reviews)} reviews have star ratings")
        
        if not unique_reviews:
            return [{"text": "ERROR: Tidak ada ulasan yang berhasil diekstrak dari semua halaman yang diakses.", "rating": None, "has_rating": False}]

    except Exception as e:
        logger.error(f"[REVIEWS] Fatal error during scraping: {type(e).__name__}: {str(e)}")
        return [{"text": f"ERROR: Terjadi kesalahan fatal saat scraping - {type(e).__name__}: {str(e)}", "rating": None, "has_rating": False}]
    finally:
        driver.quit()
    
    # Limit to max_reviews if we got more than needed
    if len(unique_reviews) > max_reviews:
        unique_reviews = unique_reviews[:max_reviews]
        logger.info(f"[REVIEWS] Limiting results to {max_reviews} reviews as requested")

    logger.info(f"[REVIEWS] Final result: Returning {len(unique_reviews)} reviews")
    return unique_reviews

def scrape_product_with_seller_reputation(url: str, max_reviews: int = 50) -> dict:
    """
    Comprehensive scraping that includes product metadata, reviews, and seller reputation.
    Returns all data needed for complete analysis.
    """
    try:
        logger.info(f"[COMPREHENSIVE] Starting comprehensive analysis for: {url}")
        
        # 1. Get product metadata
        metadata = scrape_product_metadata(url)
        logger.info(f"[COMPREHENSIVE] Product metadata scraped: {metadata.get('product_title', 'Unknown')}")
        
        # 2. Get reviews with ratings
        reviews_data = scrape_product_reviews(url, max_reviews)
        logger.info(f"[COMPREHENSIVE] Reviews scraped: {len(reviews_data)} reviews")
        
        # 3. Get seller reputation
        seller_reputation = analyze_seller_reputation(url)
        logger.info(f"[COMPREHENSIVE] Seller reputation analyzed: {seller_reputation.get('reliability_score', 'N/A')} score")
        
        return {
            "metadata": metadata,
            "reviews_data": reviews_data,
            "seller_reputation": seller_reputation
        }
        
    except Exception as e:
        logger.error(f"[COMPREHENSIVE] Error in comprehensive scraping: {str(e)}")
        return {
            "metadata": {"error": f"Metadata extraction failed: {str(e)}"},
            "reviews_data": [{"text": f"Review extraction failed: {str(e)}", "rating": None, "has_rating": False}],
            "seller_reputation": {"error": f"Seller reputation analysis failed: {str(e)}"}
        }