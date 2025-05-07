from flask import Flask, jsonify
from dataextract import scrape_pagasa_water_level
from pagasa_scraper import scrape_pagasa_rainfall
from datetime import datetime
import os
import logging
from threading import Lock

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add rate limiting
scrape_lock = Lock()
LAST_SCRAPE_TIME = 0
MIN_SCRAPE_INTERVAL = 300  # 5 minutes

@app.route('/api/water-level', methods=['GET'])
def get_water_level():
    global LAST_SCRAPE_TIME
    
    with scrape_lock:
        current_time = time.time()
        if current_time - LAST_SCRAPE_TIME < MIN_SCRAPE_INTERVAL:
            return jsonify({
                "status": "error",
                "message": "Please wait before making another request",
                "timestamp": datetime.now().isoformat()
            }), 429
            
        LAST_SCRAPE_TIME = current_time
        logger.info("Processing water level request")
        
        try:
            headers, data = scrape_pagasa_water_level()
            
            if data:
                logger.info(f"Successfully retrieved {len(data)} records")
                return jsonify({
                    "status": "success",
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                    "record_count": len(data)
                })
            else:
                logger.error("Failed to fetch water level data (no data returned)")
                return jsonify({
                    "status": "error",
                    "message": "Scraper returned no data - check server logs",
                    "timestamp": datetime.now().isoformat()
                }), 500
                
        except Exception as e:
            logger.error(f"API ERROR: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Internal server error",
                "timestamp": datetime.now().isoformat()
            }), 500

# Similar implementation for rainfall endpoint

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))