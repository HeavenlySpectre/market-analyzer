from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import logging
from urllib.parse import urljoin, urlparse
from typing import Dict, Optional, Any

# Configure logging for seller reputation
logger = logging.getLogger(__name__)

class SellerReputationAnalyzer:
    def __init__(self):
        self.cache = {}  # Simple in-memory cache for demo
        self.cache_ttl = 24 * 60 * 60  # 24 hours in seconds
        
    def get_seller_reputation(self, product_url: str) -> Dict[str, Any]:
        """
        Extract comprehensive seller reputation data from Tokopedia PDP and shop page.
        """
        try:
            # Check cache first
            cache_key = self._get_shop_cache_key(product_url)
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    logger.info(f"[SELLER] Using cached reputation data for {cache_key}")
                    return cached_data
            
            # Setup Chrome driver
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--log-level=3")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            wait = WebDriverWait(driver, 15)
            
            try:
                # Step 1: Extract PDP-level seller info
                logger.info(f"[SELLER] Analyzing seller reputation for: {product_url}")
                
                # Check if URL is valid
                if not product_url.startswith('http'):
                    logger.error(f"[SELLER] Invalid URL format: {product_url}")
                    raise ValueError("Invalid URL format")
                
                driver.get(product_url)
                
                # Wait for page to load and check if we got the actual page
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Check if we got redirected to an error page
                current_url = driver.current_url
                if "tokopedia.com" not in current_url:
                    logger.warning(f"[SELLER] Redirected to non-Tokopedia page: {current_url}")
                
                # Wait specifically for Tokopedia content to appear
                try:
                    # Wait for any Tokopedia-specific elements
                    wait.until(lambda d: 
                        d.find_elements(By.CSS_SELECTOR, '[data-testid]') or
                        d.find_elements(By.CSS_SELECTOR, 'img[src*="tokopedia"]') or
                        d.find_elements(By.XPATH, "//div[contains(@class, 'css-')]") or
                        "tokopedia" in d.page_source.lower()
                    )
                    logger.info("[SELLER] Tokopedia content detected")
                except Exception as e:
                    logger.warning(f"[SELLER] Tokopedia content wait timed out: {e}")
                
                # Additional wait for dynamic content
                time.sleep(5)  # Allow more time for dynamic content to load
                
                # Check page source for Tokopedia content
                page_source = driver.page_source
                if "tokopedia" not in page_source.lower():
                    logger.warning("[SELLER] Page source doesn't contain Tokopedia content")
                    logger.info(f"[SELLER] Current URL: {driver.current_url}")
                    logger.info(f"[SELLER] Page title: {driver.title}")
                
                soup = BeautifulSoup(page_source, 'html.parser')
                reputation_data = self._extract_pdp_seller_info(soup)
                
                # Step 2: Try to get shop page URL and extract additional metrics
                shop_url = self._find_shop_url(soup, product_url)
                if shop_url:
                    try:
                        logger.info(f"[SELLER] Navigating to shop page: {shop_url}")
                        driver.get(shop_url)
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        time.sleep(3)
                        
                        shop_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        shop_metrics = self._extract_shop_metrics(shop_soup)
                        reputation_data.update(shop_metrics)
                        
                    except Exception as e:
                        logger.warning(f"[SELLER] Could not extract shop metrics: {str(e)}")
                        reputation_data["notes"].append("Shop page metrics unavailable")
                
                # Step 3: Calculate reliability score
                reputation_data = self._calculate_reliability_score(reputation_data)
                
                # Cache the result
                if cache_key:
                    self.cache[cache_key] = (reputation_data, time.time())
                
                logger.info(f"[SELLER] Seller analysis complete. Score: {reputation_data.get('reliability_score', 'N/A')}")
                return reputation_data
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"[SELLER] Error analyzing seller reputation: {str(e)}")
            return self._get_fallback_reputation_data(str(e))
    
    def _extract_pdp_seller_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract seller information visible on the PDP."""
        data = {
            "seller_name": None,
            "badges": [],
            "store_rating": None,
            "followers": None,
            "product_count": None,
            "chat_performance": None,
            "on_time_shipping": None,
            "cancellation_rate": None,
            "join_date": None,
            "location": None,
            "processing_time": None,
            "notes": [],
            "components": {}
        }
        
        logger.info("[SELLER] Starting PDP extraction...")
        
        # Debug: Save HTML to file for inspection if extraction fails
        try:
            import os
            debug_dir = "debug_html"
            os.makedirs(debug_dir, exist_ok=True)
            with open(os.path.join(debug_dir, "tokopedia_page.html"), "w", encoding="utf-8") as f:
                f.write(str(soup))
            logger.info("[SELLER] HTML content saved to debug_html/tokopedia_page.html for inspection")
        except Exception as debug_e:
            logger.warning(f"[SELLER] Could not save debug HTML: {debug_e}")
        
        # Debug: Log all elements with class containing 'css-b6ktge'
        debug_elements = soup.find_all(class_=re.compile(r'css-b6ktge'))
        logger.info(f"[SELLER] Found {len(debug_elements)} elements with css-b6ktge class")
        
        # Also try finding by text content
        all_divs = soup.find_all('div')
        matching_divs = []
        for div in all_divs:
            if div.get('class') and any('css-b6ktge' in str(cls) for cls in div.get('class')):
                matching_divs.append(div)
        logger.info(f"[SELLER] Found {len(matching_divs)} divs with css-b6ktge in class list")
        
        # Extract shop name and badges
        shop_container = soup.select_one('[data-testid="llbPDPFooterShopName"]')
        if shop_container:
            # Shop name
            shop_name_element = shop_container.select_one('h2')
            if shop_name_element:
                data["seller_name"] = shop_name_element.get_text(strip=True)
                logger.info(f"[SELLER] Shop name found: {data['seller_name']}")
            
            # Official Store badge
            if shop_container.select_one('[data-testid="pdpShopBadgeOS"]'):
                data["badges"].append("OFFICIAL_STORE")
                logger.info("[SELLER] Official Store badge detected")
            
            # Power Merchant badges (look for other badge images)
            power_merchant_badges = shop_container.select('img[src*="power_merchant"], img[src*="badge"]')
            for badge in power_merchant_badges:
                src = badge.get('src', '')
                alt = badge.get('alt', '').lower()
                if 'power_merchant_pro' in src or 'pro' in alt:
                    data["badges"].append("POWER_MERCHANT_PRO")
                    logger.info("[SELLER] Power Merchant PRO badge detected")
                elif 'power_merchant' in src or 'merchant' in alt:
                    data["badges"].append("POWER_MERCHANT")
                    logger.info("[SELLER] Power Merchant badge detected")
        
        # Extract shop credibility info directly from grid rows
        # Look for grid rows with star and clock icons
        grid_rows = soup.select('div[data-unify="grid"][class*="grid-row"]')
        logger.info(f"[SELLER] Found {len(grid_rows)} grid rows")
        
        # Process each grid row to find rating and processing time
        for row in grid_rows:
            # Look for rating information (star icon + rating text)
            star_icon = row.select_one('img[src*="action-star"]')
            if star_icon:
                logger.info("[SELLER] Found star icon in grid row")
                # Find the rating text in the same row
                rating_text_element = row.select_one('p')
                if rating_text_element:
                    rating_spans = rating_text_element.select('span')
                    for i, span in enumerate(rating_spans):
                        span_text = span.get_text(strip=True)
                        
                        # First span should be the rating (e.g., "4.9")
                        if i == 0:
                            try:
                                rating_value = float(span_text)
                                if 0 <= rating_value <= 5:
                                    data["store_rating"] = rating_value
                                    logger.info(f"[SELLER] Store rating extracted: {rating_value}")
                            except ValueError:
                                pass
                        
                        # Second span should be review count (e.g., "(6 rb)")
                        elif i == 1:
                            # Extract number and suffix from parentheses
                            review_match = re.search(r'\(([0-9,]+(?:\.[0-9]+)?)\s*(rb|k|ribu|jt|juta)?\)', span_text)
                            if review_match:
                                count_str = review_match.group(1).replace(',', '')
                                suffix = review_match.group(2)
                                try:
                                    count = float(count_str)
                                    if suffix in ['rb', 'k', 'ribu']:
                                        count *= 1000
                                    elif suffix in ['jt', 'juta']:
                                        count *= 1000000
                                    data["followers"] = int(count)
                                    logger.info(f"[SELLER] Review count extracted: {data['followers']}")
                                except (ValueError, TypeError):
                                    pass
            
            # Look for processing time information (clock icon + time text)  
            clock_icon = row.select_one('img[src*="general-clock"]')
            if clock_icon:
                logger.info("[SELLER] Found clock icon in grid row")
                time_text_element = row.select_one('p')
                if time_text_element:
                    # Extract the processing time text
                    time_spans = time_text_element.select('span')
                    if time_spans:
                        time_text = time_spans[0].get_text(strip=True)  # "± 55 menit"
                        data["processing_time"] = time_text
                        logger.info(f"[SELLER] Processing time extracted: {time_text}")
        
        # Fallback: Content-based extraction
        if not data["store_rating"]:
            logger.info("[SELLER] Trying content-based extraction...")
            text = soup.get_text()
            
            # Look for rating patterns in the full text
            rating_pattern = re.search(r'(\d+\.\d+)\s*\(([0-9,]+(?:\.[0-9]+)?)\s*(rb|k|ribu|jt|juta)?\)', text)
            if rating_pattern:
                try:
                    rating = float(rating_pattern.group(1))
                    if 0 <= rating <= 5:
                        data["store_rating"] = rating
                        logger.info(f"[SELLER] Content-based rating extracted: {rating}")
                        
                        # Extract review count from same pattern
                        count_str = rating_pattern.group(2).replace(',', '')
                        suffix = rating_pattern.group(3)
                        count = float(count_str)
                        if suffix in ['rb', 'k', 'ribu']:
                            count *= 1000
                        elif suffix in ['jt', 'juta']:
                            count *= 1000000
                        data["followers"] = int(count)
                        logger.info(f"[SELLER] Content-based review count extracted: {data['followers']}")
                except (ValueError, TypeError):
                    pass
        else:
            logger.warning("[SELLER] Credibility container not found with selector .css-b6ktge")
            
            # Fallback: Search for rating and processing time by content patterns
            logger.info("[SELLER] Trying content-based extraction...")
            
            # Look for rating patterns anywhere on the page
            all_text_elements = soup.find_all(['span', 'p', 'div'])
            for element in all_text_elements:
                text = element.get_text(strip=True)
                
                # Look for rating pattern with parentheses (e.g., "4.9 (6 rb)")
                rating_pattern = re.search(r'(\d+\.?\d*)\s*\(([0-9,]+(?:\.[0-9]+)?)\s*(rb|k|ribu|jt|juta)?\)', text)
                if rating_pattern and not data["store_rating"]:
                    try:
                        rating = float(rating_pattern.group(1))
                        if 0 <= rating <= 5:
                            data["store_rating"] = rating
                            logger.info(f"[SELLER] Content-based rating extracted: {rating}")
                            
                            # Extract review count from same pattern
                            count_str = rating_pattern.group(2).replace(',', '')
                            suffix = rating_pattern.group(3)
                            count = float(count_str)
                            if suffix in ['rb', 'k', 'ribu']:
                                count *= 1000
                            elif suffix in ['jt', 'juta']:
                                count *= 1000000
                            data["followers"] = int(count)
                            logger.info(f"[SELLER] Content-based review count extracted: {data['followers']}")
                    except (ValueError, TypeError):
                        pass
                
                # Look for processing time patterns
                time_pattern = re.search(r'[±]\s*(\d+)\s*(menit|jam|hari)', text)
                if time_pattern and not data["processing_time"]:
                    data["processing_time"] = text
                    logger.info(f"[SELLER] Content-based processing time extracted: {text}")
            
            # If still nothing found, add note
            if not data["store_rating"] and not data["processing_time"]:
                data["notes"].append("Seller metrics not found in expected locations")
        
        return data
    
    def _find_shop_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Try to find the shop/seller page URL from the PDP."""
        # Look for common shop link patterns
        shop_link_selectors = [
            'a[href*="/shop/"]',
            'a[href*="/seller/"]',
            '[data-testid*="shop"] a',
            '[data-testid*="seller"] a'
        ]
        
        for selector in shop_link_selectors:
            link = soup.select_one(selector)
            if link and link.get('href'):
                href = link.get('href')
                # Make absolute URL
                if href.startswith('/'):
                    return urljoin(base_url, href)
                elif href.startswith('http'):
                    return href
        
        logger.warning("[SELLER] Could not find shop page URL")
        return None
    
    def _extract_shop_metrics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed metrics from the shop page."""
        metrics = {}
        
        # Look for various shop metrics
        # This would need to be implemented based on actual shop page structure
        # For now, return empty metrics with note
        metrics["notes"] = ["Shop page structure analysis needed"]
        
        return metrics
    
    def _calculate_reliability_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate reliability score using the improved algorithm:
        - Quality (50%): Bayesian-smoothed rating
        - Operations (30%): Chat/shipping/cancellation (neutral 70 if missing)
        - Trust (20%): Badges + tenure + popularity
        - Confidence: Coverage-based confidence score
        """
        import math
        
        components = {}
        confidence_factors = {}
        
        # === 1. QUALITY (50%): Bayesian-smoothed rating ===
        quality_score = 0.0
        if data["store_rating"] and data.get("followers"):
            # Bayesian smoothing parameters
            prior_rating = 4.0  # Conservative prior for Indonesian e-commerce
            confidence_threshold = 50  # Reviews needed for full confidence in observed rating
            
            observed_rating = data["store_rating"]
            review_count = data["followers"] or 0
            
            # Bayesian adjustment: more reviews = closer to observed rating
            weight = min(1.0, review_count / confidence_threshold)
            adjusted_rating = (weight * observed_rating) + ((1 - weight) * prior_rating)
            
            quality_score = (adjusted_rating / 5.0) * 50  # 50% weight
            components["quality"] = {
                "score": round(quality_score, 1),
                "observed_rating": observed_rating,
                "adjusted_rating": round(adjusted_rating, 2),
                "review_count": review_count,
                "weight": round(weight, 2)
            }
            confidence_factors["quality"] = 1.0  # Full confidence when we have rating + volume
        elif data["store_rating"]:
            # Rating without volume data - less confident
            adjusted_rating = (0.7 * data["store_rating"]) + (0.3 * 4.0)  # Blend with prior
            quality_score = (adjusted_rating / 5.0) * 50
            components["quality"] = {
                "score": round(quality_score, 1),
                "observed_rating": data["store_rating"],
                "adjusted_rating": round(adjusted_rating, 2),
                "review_count": 0,
                "note": "Volume data missing - conservative adjustment applied"
            }
            confidence_factors["quality"] = 0.7  # Reduced confidence without volume
        else:
            # No rating data - neutral assumption
            quality_score = (4.0 / 5.0) * 50  # Neutral 4.0 rating assumption
            components["quality"] = {
                "score": round(quality_score, 1),
                "note": "Rating data missing - neutral assumption (4.0/5)"
            }
            confidence_factors["quality"] = 0.3  # Low confidence
        
        # === 2. OPERATIONS (30%): Chat/Shipping/Cancellation ===
        operations_score = 0.0
        ops_coverage = 0.0
        
        # Chat performance (15% of total = 50% of operations)
        if data.get("chat_performance"):
            chat_score = data["chat_performance"] * 0.15
            operations_score += chat_score
            components["chat"] = round(chat_score, 1)
            ops_coverage += 0.50
        else:
            # Missing - use neutral 70
            chat_score = 70 * 0.15
            operations_score += chat_score
            components["chat"] = {"score": round(chat_score, 1), "note": "Missing - neutral assumption"}
        
        # On-time shipping (10% of total = 33% of operations)  
        if data.get("on_time_shipping"):
            shipping_score = data["on_time_shipping"] * 0.10
            operations_score += shipping_score
            components["shipping"] = round(shipping_score, 1)
            ops_coverage += 0.33
        else:
            shipping_score = 70 * 0.10
            operations_score += shipping_score
            components["shipping"] = {"score": round(shipping_score, 1), "note": "Missing - neutral assumption"}
        
        # Cancellation rate (5% of total = 17% of operations)
        if data.get("cancellation_rate"):
            cancel_score = (100 - data["cancellation_rate"]) * 0.05  # Lower cancellation = higher score
            operations_score += cancel_score
            components["cancellation"] = round(cancel_score, 1)
            ops_coverage += 0.17
        else:
            cancel_score = (100 - 30) * 0.05  # Assume neutral 30% cancellation
            operations_score += cancel_score
            components["cancellation"] = {"score": round(cancel_score, 1), "note": "Missing - neutral assumption"}
        
        confidence_factors["operations"] = ops_coverage
        
        # === 3. TRUST (20%): Badges + Tenure + Popularity ===
        trust_score = 0.0
        
        # Badges (up to 12 points)
        badge_score = 0.0
        if "OFFICIAL_STORE" in data.get("badges", []):
            badge_score = 12.0
        elif "POWER_MERCHANT_PRO" in data.get("badges", []):
            badge_score = 8.0
        elif "POWER_MERCHANT" in data.get("badges", []):
            badge_score = 5.0
        
        # Tenure (up to 5 points) - based on join date if available
        tenure_score = 0.0
        if data.get("join_date"):
            # TODO: Calculate actual tenure when date parsing is implemented
            tenure_score = 0.0  # Placeholder
        
        # Popularity (up to 3 points) - log scale of followers/products
        popularity_score = 0.0
        if data.get("followers"):
            # Log scale: 1k followers = ~1 point, 10k = ~2 points, 100k+ = 3 points
            popularity_score = min(3.0, math.log10(max(1, data["followers"])) - 1)
            popularity_score = max(0.0, popularity_score)
        
        trust_score = badge_score + tenure_score + popularity_score
        trust_score = min(20.0, trust_score)  # Cap at 20
        
        components["trust"] = {
            "total": round(trust_score, 1),
            "badges": round(badge_score, 1),
            "tenure": round(tenure_score, 1), 
            "popularity": round(popularity_score, 1)
        }
        confidence_factors["trust"] = 1.0 if badge_score > 0 else 0.5  # High confidence if badges present
        
        # === FINAL SCORE CALCULATION ===
        total_score = quality_score + operations_score + trust_score
        
        # === CONFIDENCE CALCULATION ===
        # Weight factors by their contribution to total score
        weighted_confidence = (
            (confidence_factors["quality"] * 0.50) + 
            (confidence_factors["operations"] * 0.30) + 
            (confidence_factors["trust"] * 0.20)
        ) * 100
        
        # === COVERAGE-AWARE CAP ===
        if ops_coverage < 0.5:  # Less than 50% operations coverage
            total_score = min(total_score, 90)  # Cap at 90
            cap_reason = "Limited operations data"
        else:
            cap_reason = None
        
        # Final bounds
        total_score = max(0, min(100, total_score))
        confidence = max(0, min(100, weighted_confidence))
        
        # Update data with results
        data["reliability_score"] = round(total_score, 1)
        data["confidence_score"] = round(confidence, 1)
        data["components"] = components
        data["coverage_info"] = {
            "operations_coverage": round(ops_coverage * 100, 1),
            "cap_applied": cap_reason
        }
        
        # Generate explanation
        explanation_parts = []
        if badge_score > 0:
            badge_names = {
                "OFFICIAL_STORE": "Official Store",
                "POWER_MERCHANT_PRO": "Power Merchant PRO", 
                "POWER_MERCHANT": "Power Merchant"
            }
            for badge in data.get("badges", []):
                if badge in badge_names:
                    explanation_parts.append(badge_names[badge])
        
        if data.get("store_rating"):
            explanation_parts.append(f"{data['store_rating']}/5 rating")
            
        if data.get("followers"):
            if data["followers"] >= 1000:
                explanation_parts.append(f"{data['followers']/1000:.1f}k reviews")
            else:
                explanation_parts.append(f"{data['followers']} reviews")
        
        # Add confidence qualifier
        confidence_qualifier = ""
        if confidence < 60:
            confidence_qualifier = " (low confidence - limited data)"
        elif confidence < 80:
            confidence_qualifier = " (moderate confidence - some data missing)"
        
        data["score_explanation"] = (", ".join(explanation_parts) if explanation_parts else "Limited data available") + confidence_qualifier
        
        return data
    
    def _get_shop_cache_key(self, product_url: str) -> Optional[str]:
        """Generate a cache key based on the shop/seller identifier."""
        try:
            parsed = urlparse(product_url)
            # Extract shop identifier from URL if possible
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                return f"shop_{path_parts[0]}_{path_parts[1]}"
            return f"shop_{parsed.netloc}_{hash(product_url) % 10000}"
        except Exception:
            return None
    
    def _get_fallback_reputation_data(self, error_msg: str) -> Dict[str, Any]:
        """Return minimal reputation data when extraction fails."""
        return {
            "seller_name": "Unknown Seller",
            "badges": [],
            "store_rating": None,
            "followers": None,
            "product_count": None,
            "chat_performance": None,
            "on_time_shipping": None,
            "cancellation_rate": None,
            "join_date": None,
            "location": None,
            "processing_time": None,
            "reliability_score": 0,
            "components": {},
            "score_explanation": "Data unavailable",
            "notes": [f"Error: {error_msg}"]
        }

# Global instance
seller_analyzer = SellerReputationAnalyzer()

def analyze_seller_reputation(product_url: str) -> Dict[str, Any]:
    """Main function to analyze seller reputation."""
    return seller_analyzer.get_seller_reputation(product_url)
