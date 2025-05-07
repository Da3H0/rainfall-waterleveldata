from flask import Flask, jsonify
from dataextract import scrape_pagasa_water_level
from pagasa_scraper import scrape_pagasa_rainfall
from datetime import datetime
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/water-level', methods=['GET'])
def get_water_level():
    """API endpoint for water level data"""
    logger.info("Processing water level request")
    headers, data = scrape_pagasa_water_level()
    
    if data:
        logger.info(f"Successfully retrieved data for {len(data)} stations")
        return jsonify({
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "stations_count": len(data)
        })
    else:
        logger.error("Failed to fetch water level data")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch data - check server logs",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/rainfall', methods=['GET'])
def get_rainfall():
    """API endpoint for rainfall data"""
    logger.info("Processing rainfall request")
    headers, data = scrape_pagasa_rainfall()
    
    if data:
        logger.info(f"Successfully retrieved data for {len(data)} stations")
        return jsonify({
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "stations_count": len(data)
        })
    else:
        logger.error("Failed to fetch rainfall data")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch data - check server logs",
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))