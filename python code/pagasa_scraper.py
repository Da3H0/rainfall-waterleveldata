from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import logging
from seleniumwire import webdriver as wire_webdriver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_driver():
    """Initialize WebDriver with Railway-compatible settings"""
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Different user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'user-agent={user_agents[1]}')
        
        # Railway-specific configuration
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            options.binary_location = '/usr/bin/google-chrome'
            driver = wire_webdriver.Chrome(options=options)
        else:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            driver = wire_webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
        
        return driver
        
    except Exception as e:
        logger.error(f"DRIVER INIT ERROR: {str(e)}")
        raise

def scrape_pagasa_rainfall():
    """Scrapes the rainfall data table from PAGASA website"""
    driver = None
    try:
        driver = init_driver()
        logger.info("Driver initialized successfully for rainfall data")
        
        url = "https://pasig-marikina-tullahanffws.pagasa.dost.gov.ph/rainfall/map.do"
        logger.info(f"Navigating to {url}")
        
        driver.get(url)
        
        # Wait for either the table or a potential error
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-type1"))
            )
            logger.info("Rainfall table element found")
        except Exception as e:
            logger.error(f"Rainfall table not found. Page title: {driver.title}")
            logger.error(f"Current URL: {driver.current_url}")
            logger.error(f"Page source (first 500 chars): {driver.page_source[:500]}")
            return None, None
        
        time.sleep(3)  # Additional buffer time
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        table = soup.find('table', {'class': 'table-type1'})
        if not table:
            logger.error("Rainfall table not found in parsed HTML")
            return None, None
        
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        
        data = []
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 3:
                data.append({
                    'Station': cols[0].get_text(strip=True),
                    'RF [mm] 1 Hour': cols[1].get_text(strip=True),
                    'RF [mm] Daily Sum(24hr)': cols[2].get_text(strip=True),
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        
        logger.info(f"Successfully scraped {len(data)} rainfall records")
        return headers, data
        
    except WebDriverException as e:
        logger.error(f"RAINFALL WEBDRIVER ERROR: {str(e)}")
        if driver:
            logger.error(f"Browser logs: {driver.get_log('browser')}")
        return None, None
    except Exception as e:
        logger.error(f"RAINFALL UNEXPECTED ERROR: {str(e)}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Line {exc_tb.tb_lineno}: {str(e)}")
        return None, None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def display_rainfall_data(headers, data):
    """Displays the rainfall data in table format"""
    if not data:
        print("No rainfall data available")
        return
    
    timestamp = data[0]['Timestamp'] if data else datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n# Time : {timestamp}")
    print("| Station | RF [mm] 1 Hour | RF [mm] Daily Sum(24hr) |")
    print("|---|---|---|")
    
    for entry in data:
        print(f"| {entry['Station']} | {entry['RF [mm] 1 Hour']} | {entry['RF [mm] Daily Sum(24hr)']} |")

def save_to_csv(data):
    """Saves the data to CSV file"""
    if not data:
        print("No rainfall data to save")
        return
    
    df = pd.DataFrame(data)
    filename = f"pagasa_rainfall_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")

if __name__ == "__main__":
    # For local testing
    print("Testing PAGASA Rainfall Scraper Locally")
    headers, data = scrape_pagasa_rainfall()
    display_rainfall_data(headers, data)
    
    if data and input("\nSave to CSV? (y/n): ").lower() == 'y':
        save_to_csv(data)