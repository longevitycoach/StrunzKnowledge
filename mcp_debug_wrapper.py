#!/usr/bin/env python3
"""
MCP Debug Wrapper - Logs all stdio communication for debugging
Based on: https://modelcontextprotocol.io/docs/tools/debugging
"""

import sys
import json
import os
from datetime import datetime
import threading
import queue

# Set up logging
LOG_FILE = os.path.expanduser("~/Desktop/mcp_debug.log")

def log_message(direction, data):
    """Log messages with timestamp"""
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} [{direction}] {data}\n")
        f.flush()

def main():
    """Main debug wrapper"""
    # Log startup
    log_message("STARTUP", f"MCP Debug Wrapper Started - PID: {os.getpid()}")
    log_message("STARTUP", f"Python: {sys.executable}")
    log_message("STARTUP", f"Working Dir: {os.getcwd()}")
    
    # Import after logging setup
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Create queues for communication
        stdin_queue = queue.Queue()
        stdout_queue = queue.Queue()
        
        # Start stdin reader thread
        def read_stdin():
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        break
                    log_message("STDIN", line.strip())
                    stdin_queue.put(line)
                except Exception as e:
                    log_message("ERROR", f"stdin error: {e}")
                    break
                    
        stdin_thread = threading.Thread(target=read_stdin, daemon=True)
        stdin_thread.start()
        
        # Import enhanced server
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        server = StrunzKnowledgeMCP()
        
        # Override FastMCP's run method to intercept messages
        original_run = server.app.run
        
        def debug_run():
            log_message("SERVER", "Starting FastMCP server in stdio mode")
            
            # Ensure stdio mode
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            
            # Add debug hooks if possible
            if hasattr(server.app, '_transport'):
                log_message("SERVER", f"Transport: {server.app._transport}")
                
            # Check capabilities
            log_message("SERVER", "Checking server capabilities...")
            
            # Start the server
            try:
                original_run()
            except Exception as e:
                log_message("ERROR", f"Server error: {e}")
                import traceback
                log_message("ERROR", traceback.format_exc())
                
        # Run with debugging
        debug_run()
        
    except Exception as e:
        log_message("FATAL", f"Fatal error: {e}")
        import traceback
        log_message("FATAL", traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    # Ensure unbuffered output
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Create log file
    with open(LOG_FILE, "w") as f:
        f.write(f"=== MCP Debug Log Started at {datetime.now().isoformat()} ===\n")
    
    print(f"Debug log will be written to: {LOG_FILE}", file=sys.stderr)
    
    main()