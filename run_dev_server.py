#!/usr/bin/env python3
"""
Development server with auto-reload for frontend changes
"""
import os
import sys
import time
import logging
import subprocess
import signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontendChangeHandler(FileSystemEventHandler):
    """Handle frontend file changes"""
    
    def __init__(self):
        self.last_reload = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Check if it's a frontend file
        if any(event.src_path.endswith(ext) for ext in ['.html', '.js', '.css']):
            current_time = time.time()
            # Debounce - only reload once per second
            if current_time - self.last_reload > 1:
                self.last_reload = current_time
                logger.info(f"Detected change in: {event.src_path}")
                logger.info("✨ Frontend files updated - refresh your browser!")

def run_servers():
    """Run both frontend and backend servers"""
    
    # Start backend server
    logger.info("Starting backend server on http://localhost:8000")
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        env={**os.environ, "PORT": "8000"}
    )
    
    # Start frontend server
    logger.info("Starting frontend server on http://localhost:8080")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd="frontend"
    )
    
    # Set up file watcher
    event_handler = FrontendChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='frontend', recursive=True)
    observer.start()
    
    logger.info("\n🚀 Development servers started!")
    logger.info("📱 Frontend: http://localhost:8080")
    logger.info("🔧 Backend: http://localhost:8000") 
    logger.info("👁️  Watching for frontend changes...")
    logger.info("\n💡 Tips:")
    logger.info("- Frontend changes are detected automatically")
    logger.info("- Just refresh your browser (Cmd+R) after changes")
    logger.info("- For hard refresh use Cmd+Shift+R")
    logger.info("- Press Ctrl+C to stop servers\n")
    
    def signal_handler(sig, frame):
        logger.info("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        observer.stop()
        observer.join()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    # Check if watchdog is installed
    try:
        import watchdog
    except ImportError:
        logger.error("Please install watchdog: pip install watchdog")
        sys.exit(1)
    
    run_servers()