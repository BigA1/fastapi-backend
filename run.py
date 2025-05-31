import uvicorn
import signal
import sys
import psutil
import socket
import os
import time

PORT = 8000

def kill_processes_on_port(port):
    """Kill any process using the specified port."""
    try:
        killed_pids = set()
        for proc in psutil.process_iter(['pid', 'name']):
            # Skip system processes
            if proc.pid == 0 or proc.name() == "System Idle Process":
                continue
                
            try:
                for conn in proc.net_connections(kind='inet'):
                    if conn.laddr.port == port:
                        print(f"Killing process {proc.pid} ({proc.name()}) using port {port}")
                        try:
                            proc.kill()
                            killed_pids.add(proc.pid)
                        except Exception as e:
                            print(f"Could not kill process {proc.pid}: {e}")
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
    except Exception as e:
        print(f"Error killing processes on port {port}: {e}")

def wait_for_port(port, timeout=30):
    """Wait for a port to become available."""
    start_time = time.time()
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('127.0.0.1', port))
                print(f"Port {port} is now available!")
                return True
        except socket.error:
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for port {port} to become available")
                return False
            print(f"Port {port} is still in use. Waiting... ({int(time.time() - start_time)}s)")
            time.sleep(1)

def handle_exit(signum, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Try to kill any processes using port 8000
    print(f"Checking for processes using port {PORT}...")
    kill_processes_on_port(PORT)
    
    # Wait for port to become available
    if not wait_for_port(PORT):
        print(f"Could not free port {PORT} after multiple attempts.")
        print("Please try:")
        print("1. Close any other applications that might be using port 8000")
        print("2. Restart your computer if the issue persists")
        sys.exit(1)
    
    print(f"Starting server on port {PORT}...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=PORT,
        reload=True,  # Enable auto-reload for development
        workers=1,
        log_level="info",
        timeout_keep_alive=5,
        timeout_graceful_shutdown=5
    ) 