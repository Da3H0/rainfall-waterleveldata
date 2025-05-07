from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_pagasa_rainfall():
    """Scrapes the rainfall data table from PAGASA website"""
    print("Launching browser to fetch PAGASA rainfall data...")
    
    try:
        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # Initialize browser
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://pasig-marikina-tullahanffws.pagasa.dost.gov.ph/rainfall/map.do")
        
        # Wait for table to load (adjust time as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-type1"))
        )
        time.sleep(2)  # Additional buffer time
        
        # Get the page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the rainfall data table
        table = soup.find('table', {'class': 'table-type1'})
        if not table:
            print("Error: Could not find rainfall data table")
            return None
        
        # Extract headers
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        
        # Extract table data
        data = []
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 3:  # Ensure we have all columns
                station = cols[0].get_text(strip=True)
                rf_1hr = cols[1].get_text(strip=True)
                rf_24hr = cols[2].get_text(strip=True)
                
                data.append({
                    'Station': station,
                    'RF [mm] 1 Hour': rf_1hr,
                    'RF [mm] Daily Sum(24hr)': rf_24hr,
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        
        return headers, data
    
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None, None
    finally:
        try:
            driver.quit()
        except:
            pass

def display_rainfall_data(headers, data):
    """Displays the rainfall data in the exact table format"""
    if not data:
        print("No rainfall data available")
        return
    
    # Get the timestamp from the first record
    timestamp = data[0]['Timestamp'] if data else datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n# Time : {timestamp}")
    print("| Station | RF [mm] 1 Hour | RF [mm] Daily Sum(24hr) |")
    print("|---|---|---|")
    
    for entry in data:
        station = entry['Station']
        rf_1hr = entry['RF [mm] 1 Hour']
        rf_24hr = entry['RF [mm] Daily Sum(24hr)']
        print(f"| {station} | {rf_1hr} | {rf_24hr} |")

def save_to_csv(data):
    """Saves the data to CSV file"""
    if not data:
        print("No data to save")
        return
    
    df = pd.DataFrame(data)
    filename = f"pagasa_rainfall_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")

def main():
    print("PAGASA Rainfall Data Scraper")
    print("=" * 40)
    
    # Scrape the data
    headers, rainfall_data = scrape_pagasa_rainfall()
    
    # Display the results
    display_rainfall_data(headers, rainfall_data)
    
    # Option to save to CSV
    if rainfall_data:
        save = input("\nDo you want to save this data to CSV? (y/n): ").lower()
        if save == 'y':
            save_to_csv(rainfall_data)

if __name__ == "__main__":
    # Install required packages if needed
    try:
        import pandas as pd
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'pandas'])
        import pandas as pd
    
    main()