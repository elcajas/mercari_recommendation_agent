"""
Mercari Japan Product Details Scraper

This script retrieves detailed product information from individual item pages on Mercari Japan.
Given a list of product URLs, it loads each page using Selenium (with headless Chrome) and parses the HTML
content using BeautifulSoup to extract structured details.

The extraction process includes:
1. For each product URL:
    - Opening the product page with Selenium and wait ultil the product title is loaded.
    - Parse the page source with BeautifulSoup.
2. From the parsed HTML:
    - Extracting the product title.
    - Extracting the product price.
    - Extracting the product condition.
3. Returning a list of dictionaries containing the extracted details for each product.

"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_product_details(driver: webdriver.Chrome, product_url: str) -> dict:
    """
    Load a single product page and extract its title, price, and condition using BeautifulSoup.
    """

    
    try:
        # Load the product page using Selenium. Wait until the product title is present.
        driver.get(product_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.heading__a7d91561.page__a7d91561"))
        )

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract product title
        title_tag = soup.select_one("h1.heading__a7d91561.page__a7d91561")
        title = title_tag.text.strip() if title_tag else "N/A"

        # Extract product price
        price_block = soup.select_one("div[data-testid='price']")
        price = "N/A"
        if price_block:
            # Look for the price inside the span following the currency span
            currency_span = price_block.select_one("span.currency")
            if currency_span:
                next_sibling = currency_span.find_next_sibling("span")
                if next_sibling:
                    price = next_sibling.text.strip()
        else:
            return None # Abort if price block is not found

        # Extract item condition 
        condition_tag = soup.select_one("span[data-testid='商品の状態']")
        if condition_tag:
            condition = condition_tag.text.strip()
        else:
            return None
        
        # Return structured product details
        return {
            "title": title,
            "price": price,
            "condition": condition,
            "url": product_url
        }

    except Exception as e:
        print(f"[ERROR] Failed to load {product_url}: {e}")
        return None

def list_details(urls: list, delay: int = 2) -> list:
    """
    Iterates over a list of product URLs and retrieves their details using Selenium.

    Parameters:
    - urls: List of product page URLs to scrape.
    - delay: Optional delay (in seconds) between requests
    """

    # Configure Selenium to use headless Chrome Browser with user-agent and anti-bot settings
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Loop through each URL and extract item details
    results = []
    for url in urls:
        result = get_product_details(driver, url)
        if result:
            results.append(result)
        # time.sleep(delay)  # add delay between requests

    driver.quit()
    
    return results