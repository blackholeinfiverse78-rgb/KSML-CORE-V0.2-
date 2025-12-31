#!/usr/bin/env python3
"""Simple script to run the KSML validator UI"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting KSML Validator Pro...")
    print("Press Ctrl+C to stop")

    # Find an available port
    import socket
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    
    print(f"Starting on port {port}")
    print(f"Open browser to: http://localhost:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")