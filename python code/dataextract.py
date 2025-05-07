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

def scrape_pagasa_water_level():
    """Scrapes the water level data table from PAGASA website"""
    print("Launching browser to fetch PAGASA water level data...")
    
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
        driver.get("https://pasig-marikina-tullahanffws.pagasa.dost.gov.ph/water/map.do")
        
        # Wait for table to load (adjust time as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-type1"))
        )
        time.sleep(2)  # Additional buffer time
        
        # Get the page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the water level data table
        table = soup.find('table', {'class': 'table-type1'})
        if not table:
            print("Error: Could not find water level data table")
            return None
        
        # Extract headers
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        
        # Extract table data
        data = []
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 5:  # Ensure we have all columns
                station = cols[0].get_text(strip=True)
                current = cols[1].get_text(strip=True)
                alert = cols[2].get_text(strip=True)
                alarm = cols[3].get_text(strip=True)
                critical = cols[4].get_text(strip=True)
                
                data.append({
                    'Station': station,
                    'Current [EL.m]': current,
                    'Alert [EL.m]': alert,
                    'Alarm [EL.m]': alarm,
                    'Critical [EL.m]': critical,
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