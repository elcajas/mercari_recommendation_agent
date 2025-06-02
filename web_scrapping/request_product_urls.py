"""
Mercari Japan Product Scraper

This script scrapes product item data from the Mercari Japan search results page,
given a URL constructed using Japanese keywords and filter parameters.

Since Mercari dynaminacally loads content via JavaScript and renders additional items
as you scroll, this script uses Selenium to handle the dynamic content loading.
It uses Selenium WebDriver to simulate browser interaction and trigger content loading through controlled scrolling.

The scraping process includes:
1. Opening the Mercari search URL in a headless Chrome browser.
2. Waiting for the initial product item to load on the page. 
3. Scrolling down the page to load more items dynamically.
4. Collecting the URLs of the product items displayed on the page.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_items(url: str) -> list:
    """
    Scrape product item URLs from the Mercari Japan search results page.
    """

    # Configure headless Chrome driver for scraping
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open the Mercari search URL
    driver.get(url)

    # Wait for the items to load. It waits for the presence of at least one item cell
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testid='item-cell']")))
    except:
        print("Items did not load in time.")
        driver.quit()
        exit()

    # Parameters to control scrolling behavior
    SCROLL_STEP = 500
    SCROLL_LIMIT = 1000
    scroll_y = 0
    scroll_count = 0

    # Scroll down the page to load more items dynamically
    while scroll_count < SCROLL_LIMIT:
        scroll_y += SCROLL_STEP
        driver.execute_script(f"window.scrollTo(0, {scroll_y});")

        new_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count += 1

        # Stop scrolling if we reach the bottom of the page
        if scroll_y >= new_height:
            break  

    # Extract product URLs from loaded items
    items = driver.find_elements(By.CSS_SELECTOR, "li[data-testid='item-cell'] a[href]")
    urls = [item.get_attribute("href") for item in items]
    driver.quit()

    return urls