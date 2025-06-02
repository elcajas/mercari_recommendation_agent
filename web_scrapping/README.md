# Web Scraping Module

This module is responsible for programmatically retrieving product listings and detailed product data from Mercari Japan, using Selenium for dynamic rendering and BeautifulSoup for HTML parsing. It supports the two-step scraping pipeline required for the recommendation system.

## Overview

The web scraping process is divided into two primary components:

1. **Product Search URL Extraction** (`request_product_urls.py`)
2. **Product Details Extraction** (`request_products_details.py`)

This structure enables separation of concerns between discovering product URLs and retrieving their detailed metadata (title, price, condition, etc.).

## Workflow

### 1. Search and Retrieve Product URLs

The `request_product_urls.py` module uses **Selenium** to perform a product search on Mercari and scrolls through the results page to dynamically load all visible items. It identifies each product listing using:

```html
<li data-testid="item-cell">
```

For each item, it extracts the product detail page URL from the anchor `<a>` tag. To simulate a real user session and avoid bot detection, the following practices are applied:

* **Custom user-agent**
* **Disabling automation detection features**
* **Using headless mode selectively**
* **Executing JavaScript to scroll down**:

  ```python
  driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
  ```

Additionally, scrolling continues iteratively until new items stop appearing. The module handles loading issues by waiting for the first item to be present before scrolling begins.

### 2. Extract Product Details

The `request_products_details.py` module accepts a list of product URLs and visits each page using Selenium. It then uses **BeautifulSoup** to parse the fully rendered HTML and extract relevant information.

**Main targets:**

* Title: from `h1.heading__a7d91561.page__a7d91561`
* Price: from `div[data-testid='price']`, parsing the second `<span>` element which contains the numeric value
* Condition: from a `<span data-testid="商品の状態">` tag

## Technical Details

* **Browser Automation**: [Selenium](https://www.selenium.dev/)
* **Driver Management**: [`webdriver-manager`](https://pypi.org/project/webdriver-manager/)
* **HTML Parsing**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)


## Input / Output

* Input: Mercari Japan search URL based on keywords provided by Claude
* Output:

  * A list of product URLs (step 1)
  * A list of dictionaries containing product metadata (step 2)

Example dictionary:

```python
{
  "title": "SONY ワイヤレスヘッドホン",
  "price": 1500,
  "condition": "未使用に近い",
  "url": "https://jp.mercari.com/item/m1234567890"
}
```
