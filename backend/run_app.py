#!/usr/bin/env python
# Helper script to run the Flask app in test mode

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables
os.environ['TESTE_MODE'] = '1'

# Import the app
from backend.api.app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)