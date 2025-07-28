# MCP Client Implementation Guide

## Overview
This guide provides step-by-step instructions for implementing the StrunzKnowledge MCP Client as a browser extension using TypeScript.

## Prerequisites

### Development Environment
- Node.js 18+ and npm/yarn
- TypeScript 5.0+
- Chrome/Firefox/Edge for testing
- Git for version control
- VS Code or similar IDE

### Required Accounts
- GitHub account for source control
- Google AI Studio account for Gemini API key
- Chrome Web Store developer account (for publishing)

## Project Setup

### 1. Initialize Project
```bash
# Create project directory
mkdir strunz-mcp-client
cd strunz-mcp-client

# Initialize npm project
npm init -y

# Install dependencies
npm install --save-dev \
  typescript \
  webpack webpack-cli \
  @types/chrome \
  ts-loader \
  copy-webpack-plugin \
  clean-webpack-plugin

# Initialize TypeScript
npx tsc --init
```

### 2. Project Structure
```
strunz-mcp-client/
├── src/
│   ├── background/
│   │   ├── index.ts
│   │   ├── api-client.ts
│   │   └── mcp-handler.ts
│   ├── content/
│   │   ├── index.ts
│   │   ├── ui-overlay.ts
│   │   └── dom-observer.ts
│   ├── popup/
│   │   ├── index.ts
│   │   ├── popup.html
│   │   └── popup.css
│   ├── types/
│   │   └── index.d.ts
│   └── utils/
│       ├── storage.ts
│       └── crypto.ts
├── public/
│   ├── manifest.json
│   └── icons/
├── webpack.config.js
├── tsconfig.json
└── package.json
```

### 3. TypeScript Configuration
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020", "DOM"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "resolveJsonModule": true,
    "types": ["chrome"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Core Implementation

### 1. Manifest Configuration
```json
// public/manifest.json
{
  "manifest_version": 3,
  "name": "StrunzKnowledge MCP Client",
  "version": "1.0.0",
  "description": "Access Dr. Strunz's knowledge base on any website",
  
  "permissions": [
    "storage",
    "activeTab"
  ],
  
  "host_permissions": [
    "https://generativelanguage.googleapis.com/*"
  ],
  
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "css": ["content.css"]
  }],
  
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

### 2. Storage Utilities
```typescript
// src/utils/storage.ts
export class SecureStorage {
  private static ENCRYPTION_KEY = 'strunz-mcp-client';
  
  static async setGeminiKey(key: string): Promise<void> {
    const encrypted = await this.encrypt(key);
    await chrome.storage.local.set({ geminiKey: encrypted });
  }
  
  static async getGeminiKey(): Promise<string | null> {
    const result = await chrome.storage.local.get('geminiKey');
    if (!result.geminiKey) return null;
    return await this.decrypt(result.geminiKey);
  }
  
  private static async encrypt(text: string): Promise<string> {
    // Simple encryption - in production use Web Crypto API
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    // Implement proper encryption here
    return btoa(String.fromCharCode(...data));
  }
  
  private static async decrypt(encrypted: string): Promise<string> {
    // Implement proper decryption here
    const data = atob(encrypted);
    return data;
  }
}
```

### 3. Gemini API Client
```typescript
// src/background/api-client.ts
interface GeminiRequest {
  contents: Array<{
    parts: Array<{
      text: string;
    }>;
  }>;
}

interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
}

export class GeminiClient {
  private apiKey: string;
  private baseUrl = 'https://generativelanguage.googleapis.com/v1';
  
  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }
  
  async generateContent(prompt: string): Promise<string> {
    const url = `${this.baseUrl}/models/gemini-pro:generateContent?key=${this.apiKey}`;
    
    const request: GeminiRequest = {
      contents: [{
        parts: [{
          text: prompt
        }]
      }]
    };
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status}`);
    }
    
    const data: GeminiResponse = await response.json();
    return data.candidates[0]?.content.parts[0]?.text || '';
  }
}
```

### 4. MCP Protocol Handler
```typescript
// src/background/mcp-handler.ts
import { GeminiClient } from './api-client';

export interface MCPRequest {
  id: string;
  method: string;
  params: any;
}

export interface MCPResponse {
  id: string;
  result?: any;
  error?: {
    code: number;
    message: string;
  };
}

export class MCPHandler {
  private geminiClient: GeminiClient;
  
  constructor(apiKey: string) {
    this.geminiClient = new GeminiClient(apiKey);
  }
  
  async handleRequest(request: MCPRequest): Promise<MCPResponse> {
    try {
      switch (request.method) {
        case 'search_knowledge':
          return await this.searchKnowledge(request);
        case 'get_stats':
          return await this.getStats(request);
        default:
          throw new Error(`Unknown method: ${request.method}`);
      }
    } catch (error) {
      return {
        id: request.id,
        error: {
          code: -32603,
          message: error.message
        }
      };
    }
  }
  
  private async searchKnowledge(request: MCPRequest): Promise<MCPResponse> {
    const { query, limit = 10 } = request.params;
    
    // Format prompt for Gemini to search Strunz knowledge
    const prompt = `
      As an expert on Dr. Strunz's health and nutrition knowledge, 
      search for information about: "${query}"
      
      Provide up to ${limit} relevant findings from Dr. Strunz's work,
      including specific recommendations, scientific backing, and practical advice.
      
      Format each finding with:
      - Topic/Title
      - Key Information
      - Source (book/article if known)
      - Practical Application
    `;
    
    const response = await this.geminiClient.generateContent(prompt);
    
    return {
      id: request.id,
      result: {
        query,
        results: this.parseSearchResults(response),
        timestamp: Date.now()
      }
    };
  }
  
  private parseSearchResults(response: string): any[] {
    // Parse Gemini response into structured results
    // This is a simplified version - implement proper parsing
    return [{
      title: 'Search Result',
      content: response,
      relevance: 0.95
    }];
  }
  
  private async getStats(request: MCPRequest): Promise<MCPResponse> {
    return {
      id: request.id,
      result: {
        totalSearches: 0,
        cacheSize: 0,
        lastUpdate: Date.now()
      }
    };
  }
}
```

### 5. Background Service Worker
```typescript
// src/background/index.ts
import { SecureStorage } from '../utils/storage';
import { MCPHandler } from './mcp-handler';

let mcpHandler: MCPHandler | null = null;

// Initialize handler when API key is available
async function initializeHandler() {
  const apiKey = await SecureStorage.getGeminiKey();
  if (apiKey) {
    mcpHandler = new MCPHandler(apiKey);
  }
}

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender).then(sendResponse);
  return true; // Keep message channel open for async response
});

async function handleMessage(request: any, sender: chrome.runtime.MessageSender) {
  switch (request.type) {
    case 'MCP_REQUEST':
      if (!mcpHandler) {
        await initializeHandler();
      }
      if (!mcpHandler) {
        return { error: 'No API key configured' };
      }
      return await mcpHandler.handleRequest(request.payload);
      
    case 'SET_API_KEY':
      await SecureStorage.setGeminiKey(request.apiKey);
      await initializeHandler();
      return { success: true };
      
    case 'CHECK_API_KEY':
      const hasKey = await SecureStorage.getGeminiKey() !== null;
      return { hasKey };
      
    default:
      return { error: 'Unknown message type' };
  }
}

// Initialize on startup
initializeHandler();
```

### 6. Content Script
```typescript
// src/content/index.ts
import { UIOverlay } from './ui-overlay';
import { DOMObserver } from './dom-observer';

class ContentScript {
  private overlay: UIOverlay;
  private observer: DOMObserver;
  
  constructor() {
    this.overlay = new UIOverlay();
    this.observer = new DOMObserver(this.handleTextSelection.bind(this));
  }
  
  initialize() {
    // Set up keyboard shortcuts
    document.addEventListener('keydown', this.handleKeyboard.bind(this));
    
    // Start observing DOM
    this.observer.start();
    
    // Listen for messages from popup
    chrome.runtime.onMessage.addListener(this.handleMessage.bind(this));
  }
  
  private handleKeyboard(event: KeyboardEvent) {
    // Ctrl/Cmd + Shift + S for search
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'S') {
      event.preventDefault();
      this.showSearchDialog();
    }
  }
  
  private handleTextSelection(text: string) {
    if (text.length > 3) {
      this.overlay.showQuickAction(text);
    }
  }
  
  private async showSearchDialog() {
    const query = await this.overlay.showSearchInput();
    if (query) {
      await this.performSearch(query);
    }
  }
  
  private async performSearch(query: string) {
    this.overlay.showLoading();
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'MCP_REQUEST',
        payload: {
          id: Date.now().toString(),
          method: 'search_knowledge',
          params: { query, limit: 10 }
        }
      });
      
      if (response.error) {
        this.overlay.showError(response.error.message);
      } else {
        this.overlay.showResults(response.result);
      }
    } catch (error) {
      this.overlay.showError('Search failed');
    }
  }
  
  private handleMessage(request: any, sender: any, sendResponse: Function) {
    switch (request.type) {
      case 'SEARCH':
        this.performSearch(request.query);
        break;
    }
  }
}

// Initialize content script
const contentScript = new ContentScript();
contentScript.initialize();
```

### 7. UI Overlay
```typescript
// src/content/ui-overlay.ts
export class UIOverlay {
  private container: HTMLElement | null = null;
  
  constructor() {
    this.createContainer();
  }
  
  private createContainer() {
    const container = document.createElement('div');
    container.id = 'strunz-mcp-overlay';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      width: 400px;
      max-height: 600px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      z-index: 999999;
      display: none;
      font-family: Arial, sans-serif;
    `;
    document.body.appendChild(container);
    this.container = container;
  }
  
  showQuickAction(selectedText: string) {
    if (!this.container) return;
    
    this.container.innerHTML = `
      <div style="padding: 16px;">
        <button id="strunz-search-btn" style="
          background: #4285f4;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
        ">
          Search Strunz Knowledge for "${selectedText.substring(0, 30)}..."
        </button>
      </div>
    `;
    
    this.container.style.display = 'block';
    
    document.getElementById('strunz-search-btn')?.addEventListener('click', () => {
      chrome.runtime.sendMessage({
        type: 'MCP_REQUEST',
        payload: {
          id: Date.now().toString(),
          method: 'search_knowledge',
          params: { query: selectedText, limit: 5 }
        }
      });
    });
    
    // Hide after 5 seconds
    setTimeout(() => {
      this.hide();
    }, 5000);
  }
  
  showSearchInput(): Promise<string | null> {
    return new Promise((resolve) => {
      if (!this.container) {
        resolve(null);
        return;
      }
      
      this.container.innerHTML = `
        <div style="padding: 16px;">
          <h3 style="margin: 0 0 12px 0;">Search Strunz Knowledge</h3>
          <input id="strunz-search-input" type="text" 
            placeholder="Enter your search query..." 
            style="
              width: 100%;
              padding: 8px;
              border: 1px solid #ddd;
              border-radius: 4px;
              margin-bottom: 12px;
            "
          />
          <div style="display: flex; gap: 8px;">
            <button id="strunz-search-submit" style="
              background: #4285f4;
              color: white;
              border: none;
              padding: 8px 16px;
              border-radius: 4px;
              cursor: pointer;
              flex: 1;
            ">Search</button>
            <button id="strunz-search-cancel" style="
              background: #f1f3f4;
              color: #333;
              border: none;
              padding: 8px 16px;
              border-radius: 4px;
              cursor: pointer;
              flex: 1;
            ">Cancel</button>
          </div>
        </div>
      `;
      
      this.container.style.display = 'block';
      
      const input = document.getElementById('strunz-search-input') as HTMLInputElement;
      const submitBtn = document.getElementById('strunz-search-submit');
      const cancelBtn = document.getElementById('strunz-search-cancel');
      
      input?.focus();
      
      const submit = () => {
        const query = input?.value.trim();
        this.hide();
        resolve(query || null);
      };
      
      const cancel = () => {
        this.hide();
        resolve(null);
      };
      
      submitBtn?.addEventListener('click', submit);
      cancelBtn?.addEventListener('click', cancel);
      input?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submit();
        if (e.key === 'Escape') cancel();
      });
    });
  }
  
  showLoading() {
    if (!this.container) return;
    
    this.container.innerHTML = `
      <div style="padding: 32px; text-align: center;">
        <div style="
          display: inline-block;
          width: 32px;
          height: 32px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid #4285f4;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        "></div>
        <style>
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
        <p style="margin-top: 16px; color: #666;">Searching Strunz Knowledge...</p>
      </div>
    `;
    
    this.container.style.display = 'block';
  }
  
  showResults(results: any) {
    if (!this.container) return;
    
    const resultsHtml = results.results.map((result: any) => `
      <div style="
        padding: 12px;
        border-bottom: 1px solid #eee;
      ">
        <h4 style="margin: 0 0 8px 0; color: #1a73e8;">${result.title}</h4>
        <p style="margin: 0; color: #5f6368; font-size: 14px;">
          ${result.content}
        </p>
        ${result.source ? `<p style="margin: 4px 0 0 0; color: #5f6368; font-size: 12px;">Source: ${result.source}</p>` : ''}
      </div>
    `).join('');
    
    this.container.innerHTML = `
      <div style="max-height: 600px; overflow-y: auto;">
        <div style="
          padding: 16px;
          border-bottom: 1px solid #eee;
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
          <h3 style="margin: 0;">Search Results</h3>
          <button id="strunz-close" style="
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #5f6368;
          ">×</button>
        </div>
        ${resultsHtml}
      </div>
    `;
    
    this.container.style.display = 'block';
    
    document.getElementById('strunz-close')?.addEventListener('click', () => {
      this.hide();
    });
  }
  
  showError(message: string) {
    if (!this.container) return;
    
    this.container.innerHTML = `
      <div style="padding: 16px; text-align: center;">
        <div style="
          color: #d93025;
          font-size: 48px;
          margin-bottom: 16px;
        ">⚠️</div>
        <p style="color: #d93025; margin: 0;">${message}</p>
        <button id="strunz-error-close" style="
          margin-top: 16px;
          background: #f1f3f4;
          color: #333;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
        ">Close</button>
      </div>
    `;
    
    this.container.style.display = 'block';
    
    document.getElementById('strunz-error-close')?.addEventListener('click', () => {
      this.hide();
    });
  }
  
  hide() {
    if (this.container) {
      this.container.style.display = 'none';
    }
  }
}
```

## Build Configuration

### Webpack Configuration
```javascript
// webpack.config.js
const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
  mode: 'production',
  entry: {
    background: './src/background/index.ts',
    content: './src/content/index.ts',
    popup: './src/popup/index.ts'
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js'
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js']
  },
  plugins: [
    new CleanWebpackPlugin(),
    new CopyWebpackPlugin({
      patterns: [
        { from: 'public', to: '.' }
      ]
    })
  ],
  optimization: {
    minimize: true,
    splitChunks: {
      chunks: 'async'
    }
  }
};
```

## Testing Strategy

### Unit Tests
```typescript
// tests/api-client.test.ts
import { GeminiClient } from '../src/background/api-client';

describe('GeminiClient', () => {
  it('should generate content successfully', async () => {
    const client = new GeminiClient('test-key');
    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        candidates: [{
          content: {
            parts: [{ text: 'Test response' }]
          }
        }]
      })
    });
    
    const result = await client.generateContent('test prompt');
    expect(result).toBe('Test response');
  });
});
```

### Integration Tests
```typescript
// tests/integration/extension.test.ts
import puppeteer from 'puppeteer';

describe('Extension Integration', () => {
  let browser: puppeteer.Browser;
  
  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: false,
      args: [
        `--disable-extensions-except=${path.join(__dirname, '../dist')}`,
        `--load-extension=${path.join(__dirname, '../dist')}`
      ]
    });
  });
  
  it('should show popup when icon clicked', async () => {
    const page = await browser.newPage();
    await page.goto('https://example.com');
    // Test extension functionality
  });
});
```

## Deployment

### Build for Production
```bash
# Install dependencies
npm ci

# Run tests
npm test

# Build extension
npm run build

# Create ZIP for store submission
npm run package
```

### Store Submission Checklist
- [ ] Update version in manifest.json
- [ ] Update changelog
- [ ] Take screenshots for store listing
- [ ] Write store description
- [ ] Test on all target browsers
- [ ] Submit for review

## Security Considerations

### API Key Protection
1. Never hardcode API keys
2. Encrypt keys in storage
3. Use secure communication channels
4. Implement rate limiting

### Content Security
1. Sanitize all user inputs
2. Use CSP headers
3. Avoid eval() and innerHTML
4. Validate all data from external sources

### Privacy
1. No user data collection
2. Local processing only
3. Clear privacy policy
4. Minimal permissions

## Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify key is valid in Google AI Studio
   - Check quotas and limits
   - Ensure proper permissions

2. **Extension Not Loading**
   - Check manifest syntax
   - Verify all files are included
   - Check browser console for errors

3. **Performance Issues**
   - Implement caching
   - Use Web Workers
   - Optimize bundle size

## Next Steps

1. **Phase 1: MVP** (Weeks 1-2)
   - Basic search functionality
   - Simple UI
   - Chrome support only

2. **Phase 2: Enhancement** (Weeks 3-4)
   - Advanced search features
   - Caching system
   - Firefox support

3. **Phase 3: Polish** (Weeks 5-6)
   - Performance optimization
   - UI improvements
   - Store submission