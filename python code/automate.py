from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time
import pandas as pd

def get_pagasa_data():
    url = "https://pasig-marikina-tullahanffws.pagasa.dost.gov.ph/water/map.do"
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        print("Launching browser to fetch PAGASA data...")
        # Update this path to your chromedriver location
        service = Service('/path/to/chromedriver')  # Change this path
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        print("Locating water level table...")
        # Try different selectors to find the table
        table = None
        for selector in ['table.water-level-table', 'table']:
            try:
                table = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if not table:
            raise ValueError("Could not find water level table on the page")
        
        data = []
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header
        
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:
                station = cols[0].text.strip()
                current = cols[1].text.strip().replace('(*)', '').strip()
                alert = cols[2].text.strip()
                alarm = cols[3].text.strip()
                critical = cols[4].text.strip()
                
                data.append({
                    'Station': station,
                    'Current': current,
                    'Alert': alert,
                    'Alarm': alarm,
                    'Critical': critical,
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Filter for target stations
        target_stations = ['San Mateo-1', 'Sto Nino', 'Tumana Bridge']
        filtered_data = [d for d in data if d['Station'] in target_stations]
        
        if not filtered_data:
            print("Warning: None of the target stations were found in the data")
        else:
            print("Successfully extracted data for target stations")
        
        return filtered_data
    
    except Exception as e:
        print(f"Error occurred during automation: {str(e)}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    data = get_pagasa_data()
    if data:
        print("\nSample Output:")
        for station in data:
            print(f"\nStation: {station['Station']}")
            print(f"Current Level: {station['Current']} m")
            print(f"Alert Level: {station['Alert']} m")
            print(f"Alarm Level: {station['Alarm']} m")
            print(f"Critical Level: {station['Critical']} m")
            print(f"Last Updated: {station['Timestamp']}")
    else:
        print("No data was retrieved")