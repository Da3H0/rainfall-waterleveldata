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

def scrape_pagasa_water_level():
    """Scrapes the water level data table from PAGASA website"""
    driver = None
    try:
        driver = init_driver()
        logger.info("Driver initialized successfully")
        
        url = "https://pasig-marikina-tullahanffws.pagasa.dost.gov.ph/water/map.do"
        logger.info(f"Navigating to {url}")
        
        driver.get(url)
        
        # Wait for either the table or a potential error
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-type1"))
            )
            logger.info("Table element found")
        except Exception as e:
            logger.error(f"Table not found. Page title: {driver.title}")
            logger.error(f"Current URL: {driver.current_url}")
            logger.error(f"Page source (first 500 chars): {driver.page_source[:500]}")
            return None, None
        
        time.sleep(3)  # Additional buffer time
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        table = soup.find('table', {'class': 'table-type1'})
        if not table:
            logger.error("Table not found in parsed HTML")
            return None, None
        
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        
        data = []
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 5:
                data.append({
                    'Station': cols[0].get_text(strip=True),
                    'Current [EL.m]': cols[1].get_text(strip=True),
                    'Alert [EL.m]': cols[2].get_text(strip=True),
                    'Alarm [EL.m]': cols[3].get_text(strip=True),
                    'Critical [EL.m]': cols[4].get_text(strip=True),
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        
        logger.info(f"Successfully scraped {len(data)} records")
        return headers, data
        
    except WebDriverException as e:
        logger.error(f"WEBDRIVER ERROR: {str(e)}")
        if driver:
            logger.error(f"Browser logs: {driver.get_log('browser')}")
        return None, None
    except Exception as e:
        logger.error(f"UNEXPECTED ERROR: {str(e)}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Line {exc_tb.tb_lineno}: {str(e)}")
        return None, None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def display_water_level_data(headers, data):
    """Displays the water level data in the exact table format"""
    if not data:
        print("No water level data available")
        return
    
    # Get the timestamp from the first record
    timestamp = data[0]['Timestamp'] if data else datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n# Time : {timestamp}")
    print("| Station | Current [EL.m] | Alert [EL.m] | Alarm [EL.m] | Critical [EL.m] |")
    print("|---|---|---|---|---|")
    
    for entry in data:
        station = entry['Station']
        current = entry['Current [EL.m]']
        alert = entry['Alert [EL.m]']
        alarm = entry['Alarm [EL.m]']
        critical = entry['Critical [EL.m]']
        print(f"| {station} | {current} | {alert} | {alarm} | {critical} |")

def save_to_csv(data):
    """Saves the data to CSV file"""
    if not data:
        print("No data to save")
        return
    
    df = pd.DataFrame(data)
    filename = f"pagasa_water_level_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")

def main():
    print("PAGASA Water Level Data Scraper")
    print("=" * 40)
    
    # Scrape the data
    headers, water_level_data = scrape_pagasa_water_level()
    
    # Display the results
    display_water_level_data(headers, water_level_data)
    
    # Option to save to CSV
    if water_level_data:
        save = input("\nDo you want to save this data to CSV? (y/n): ").lower()
        if save == 'y':
            save_to_csv(water_level_data)

if __name__ == "__main__":
    # Install required packages if needed
    try:
        import pandas as pd
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'pandas'])
        import pandas as pd
    
    main()