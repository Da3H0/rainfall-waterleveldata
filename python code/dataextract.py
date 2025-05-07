from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def scrape_pagasa_water_level():
    """Scrapes the water level data table from PAGASA website"""
    print("Launching browser to fetch PAGASA water level data...")
    
    try:
        # Configure Chrome options for Railway
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
        
        # Initialize browser
        driver = webdriver.Chrome(
            executable_path=os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"),
            options=options
        )
        
        # Rest of your existing code remains the same...
        driver.get("https://pasig-marikina-tullahanffws.pagasa.dost.gov.ph/water/map.do")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-type1"))
        )
        time.sleep(2)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        table = soup.find('table', {'class': 'table-type1'})
        if not table:
            print("Error: Could not find water level data table")
            return None
        
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
        
        return headers, data
    
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None, None
    finally:
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