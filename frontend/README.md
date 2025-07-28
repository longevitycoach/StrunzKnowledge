# StrunzKnowledge Chat Frontend

A standalone web-based chat interface that uses the server-side Gemini API to interact with Dr. Strunz's knowledge base. No API keys needed - just open and chat!

## Features

- 🚀 **Zero Setup**: No API keys needed - uses server-side Gemini integration
- 💬 **AI-Powered Chat**: Powered by Google's Gemini 2.5 Flash model
- 🔍 **Smart Search**: Search Dr. Strunz's books, articles, and forum posts
- 📊 **Health Analysis**: Get comprehensive analysis of health topics
- 🎨 **Modern UI**: Clean, responsive chat interface
- 🛡️ **Rate Limiting**: Built-in protection against excessive usage
- 💰 **Cost Control**: Server-side throttling to manage API costs

## Quick Start

### Option 1: Local Python Server
```bash
cd frontend
python serve.py
# Open http://localhost:8080 in your browser
```

### Option 2: Any HTTP Server
```bash
# Using Node.js http-server
npx http-server frontend -p 8080

# Using Python 3
cd frontend && python -m http.server 8080
```

### Option 3: Direct File Access
Simply open `frontend/index.html` in your browser (some features may be limited due to CORS)

## Setup

1. **Ensure Server is Running**:
   - The MCP server must be running with `GOOGLE_GEMINI_API_KEY` configured
   - Check server status at http://localhost:8000/health

2. **Open the Chat Interface**:
   - Navigate to http://localhost:8080
   - The interface will auto-connect to the server

3. **Start Chatting**:
   - Use the search tool to find specific information
   - Use "Ask Dr. Strunz" for personalized health questions
   - Use "Analyze Topic" for comprehensive health topic analysis

## Available Tools

### 🔍 Search
Search through Dr. Strunz's knowledge base for specific information about vitamins, minerals, health conditions, and more.

### 💬 Ask Dr. Strunz
Get personalized answers to your health questions based on Dr. Strunz's principles and recommendations.

### 📊 Analyze Topic
Get a comprehensive analysis of any health topic from Dr. Strunz's perspective, including nutrients, lifestyle recommendations, and practical tips.

## Technical Details

- **Frontend**: Pure HTML5, CSS3, and Vanilla JavaScript
- **AI Model**: Google Gemini 2.5 Flash (server-side)
- **API**: Server-proxied calls with rate limiting
- **Rate Limits**: 
  - 5 requests per minute per IP
  - 30 requests per hour per IP
  - $5 daily cost limit
- **MCP Server**: Required at https://strunz.up.railway.app or localhost

## Security & Rate Limiting

- No API keys stored in browser
- Server-side Gemini API key management
- Automatic rate limiting per IP address
- Daily cost controls to prevent excessive usage
- All requests proxied through secure server

## Customization

Edit these files to customize the interface:
- `styles.css` - Visual styling and themes
- `app.js` - Chat logic and API integration
- `index.html` - Page structure and layout

## Future Enhancements

- [ ] Voice input/output support
- [ ] Export chat history
- [ ] Multiple chat sessions
- [ ] Direct MCP server tool integration
- [ ] Offline caching of responses
- [ ] Multi-language support

## Troubleshooting

**Connection Issues**:
- Ensure the MCP server is running (check http://localhost:8000/health)
- Verify `GOOGLE_GEMINI_API_KEY` is set in server environment
- Check browser console for CORS errors
- Try using the Python server (`serve.py`)

**Rate Limit Errors**:
- Wait 60 seconds between requests if you hit the limit
- Check rate limit stats at http://localhost:8000/api/gemini/stats
- Daily limits reset at midnight

**No Results**:
- Try rephrasing your question
- Use more specific health-related terms
- Check server logs for Gemini API errors