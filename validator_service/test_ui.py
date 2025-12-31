#!/usr/bin/env python3
"""Test the UI by opening it in browser"""

import webbrowser
import time
import threading
import uvicorn
from main import app

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == "__main__":
    print("Starting KSML Validator UI...")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Open browser
    print("Opening browser to: http://localhost:8000")
    webbrowser.open("http://localhost:8000")
    
    print("UI is running! Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")