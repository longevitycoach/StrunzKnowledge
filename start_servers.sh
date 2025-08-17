#!/bin/bash
# Start both frontend and backend servers

echo "🚀 Starting StrunzKnowledge Servers..."

# Kill any existing processes on our ports
echo "🧹 Cleaning up any existing servers..."
pkill -f "python main.py" 2>/dev/null
pkill -f "python serve.py" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null
sleep 2

# Start backend server in background with SSE transport
echo "📡 Starting backend server on http://localhost:8000"
TRANSPORT=sse python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend server is running!"
else
    echo "❌ Backend server failed to start. Check the logs."
    exit 1
fi

# Start frontend server
echo "🌐 Starting frontend server on http://localhost:8080"
cd frontend
python serve.py &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servers started successfully!"
echo "📱 Frontend: http://localhost:8080"
echo "🔧 Backend: http://localhost:8000"
echo ""
echo "🌐 Open http://localhost:8080 in your browser"
echo "💡 If you see connection errors, try refreshing with Cmd+Shift+R"
echo ""
echo "Press Ctrl+C to stop servers..."

# Function to handle cleanup
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Set up signal handling
trap cleanup INT TERM

# Wait for user to stop
wait