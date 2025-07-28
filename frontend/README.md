# StrunzKnowledge Chat Frontend

A standalone web-based chat interface that uses the Gemini API to interact with Dr. Strunz's knowledge base. This is a true auth-less client implementation - no server authentication required, just your Gemini API key!

## Features

- 🔑 **Single Key Setup**: Just add your Gemini API key - no OAuth or complex authentication
- 💬 **AI-Powered Chat**: Direct integration with Google's Gemini 2.5 Flash model
- 🔍 **Smart Search**: Search Dr. Strunz's books, articles, and forum posts
- 📊 **Health Analysis**: Get comprehensive analysis of health topics
- 🎨 **Modern UI**: Clean, responsive chat interface
- 🔒 **Privacy First**: All processing happens in your browser
- 💾 **Local Storage**: Your API key is saved locally for convenience

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

1. **Get a Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key

2. **Open the Chat Interface**:
   - Navigate to http://localhost:8080
   - Paste your Gemini API key
   - Click "Save & Connect"

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
- **AI Model**: Google Gemini 2.5 Flash
- **API**: Direct client-side calls to Gemini API
- **Storage**: LocalStorage for API key persistence
- **MCP Server**: Optional integration with https://strunz.up.railway.app

## Security

- Your Gemini API key is stored locally in your browser
- All API calls are made directly from your browser to Google's servers
- No data is sent to any intermediate servers
- The MCP server connection is optional and read-only

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

**API Key Issues**:
- Ensure your key is valid in Google AI Studio
- Check that the Generative Language API is enabled
- Verify you haven't exceeded rate limits

**Connection Issues**:
- Check browser console for errors
- Ensure CORS is not blocking requests
- Try using the Python server (`serve.py`)

**No Results**:
- Try rephrasing your question
- Use more specific health-related terms
- Check that your API key has access to Gemini 2.5 Flash