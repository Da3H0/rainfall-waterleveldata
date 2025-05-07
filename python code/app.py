from flask import Flask, jsonify
from dataextract import scrape_pagasa_water_level
from pagasa_scraper import scrape_pagasa_rainfall
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/api/water-level', methods=['GET'])
def get_water_level():
    """API endpoint for water level data"""
    try:
        headers, data = scrape_pagasa_water_level()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data available",
                "timestamp": datetime.now().isoformat()
            }), 404
            
        return jsonify({
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/rainfall', methods=['GET'])
def get_rainfall():
    """API endpoint for rainfall data"""
    try:
        headers, data = scrape_pagasa_rainfall()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data available",
                "timestamp": datetime.now().isoformat()
            }), 404
            
        return jsonify({
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))