"""
Main Application Entry Point (Flask Webhook Server for YuedPao Chatbot)
"""

import os
import sys

# Ensure project root directory is included in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify
from app.controllers.webhook_controller import webhook_bp

# Set encoding safeguard for Windows CLI
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

# Register Webhook Blueprint
app.register_blueprint(webhook_bp)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify server status."""
    return jsonify({
        "status": "healthy",
        "service": "Chatbot YuedPao Flask Webhook Server",
        "version": "0.1.0"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
