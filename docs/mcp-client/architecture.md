# MCP Client Architecture

## Overview
This document describes the technical architecture of the StrunzKnowledge MCP Client browser extension, focusing on auth-less integration and client-side processing.

## Architecture Principles

### 1. Privacy-First Design
- All data processing happens in the browser
- No server communication except LLM API calls
- User data never leaves the client
- Gemini Key stored securely in browser storage

### 2. Universal Compatibility
- Works on any website through content script injection
- No server-side dependencies
- Minimal permissions required
- Progressive enhancement approach

### 3. Performance Optimization
- Lazy loading of components
- Efficient bundling (<500KB target)
- Web Workers for heavy processing
- Caching strategies for repeated queries

## Component Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        Browser Extension                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Popup UI  │  │Content Script│  │ Background Worker│  │
│  │             │  │              │  │                  │  │
│  │ • Settings  │  │ • Injection  │  │ • API Calls      │  │
│  │ • Search    │  │ • UI Overlay │  │ • Processing     │  │
│  │ • History   │  │ • Events     │  │ • Caching        │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │             │
│         └─────────────────┴────────────────────┘            │
│                           │                                  │
│                    Message Passing                           │
└───────────────────────────┴─────────────────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │  Gemini API    │
                   │  (LLM Backend) │
                   └────────────────┘
```

### Component Details

#### 1. Popup UI
**Purpose**: Main user interface for extension configuration and direct searches

**Technologies**:
- HTML5 + CSS3 for markup and styling
- TypeScript/JavaScript for logic
- React/Vue/Vanilla JS (TBD based on SDK evaluation)

**Features**:
- Gemini Key configuration
- Quick search interface
- Search history
- Settings management
- Usage statistics

#### 2. Content Script
**Purpose**: Injected into web pages to provide MCP functionality

**Responsibilities**:
- Detect user interactions (text selection, hotkeys)
- Inject UI overlay for search results
- Handle page-specific integration
- Communicate with background worker

**Security Considerations**:
- Isolated execution context
- Minimal DOM manipulation
- XSS prevention
- CSP compliance

#### 3. Background Worker
**Purpose**: Handle API calls and heavy processing

**Responsibilities**:
- Gemini API communication
- MCP protocol implementation
- Response caching
- State management
- Cross-tab synchronization

**Implementation**:
- Service Worker (Manifest V3)
- IndexedDB for storage
- Cache API for responses

## Data Flow

### Search Flow
```
1. User Action (text selection/hotkey)
   ↓
2. Content Script captures event
   ↓
3. Message sent to Background Worker
   ↓
4. Background Worker processes request
   ├─ Check cache
   ├─ Call Gemini API if needed
   └─ Format MCP response
   ↓
5. Response sent to Content Script
   ↓
6. Content Script displays results
```

### Configuration Flow
```
1. User opens Popup UI
   ↓
2. User enters Gemini Key
   ↓
3. Key validated with test API call
   ↓
4. Key stored in browser.storage.local
   ↓
5. All components notified of configuration
```

## Storage Architecture

### Browser Storage Layers
1. **browser.storage.local**
   - Gemini API Key (encrypted)
   - User preferences
   - Extension settings

2. **IndexedDB**
   - Search history
   - Cached responses
   - Usage analytics

3. **Session Storage**
   - Temporary state
   - Active searches
   - UI state

### Data Schemas

#### Settings Schema
```typescript
interface Settings {
  geminiKey: string;        // Encrypted
  enableCache: boolean;
  cacheExpiry: number;      // Minutes
  searchHotkey: string;
  theme: 'light' | 'dark' | 'auto';
  language: string;
}
```

#### Cache Entry Schema
```typescript
interface CacheEntry {
  query: string;
  response: MCPResponse;
  timestamp: number;
  expiresAt: number;
  source: 'gemini' | 'local';
}
```

## Security Architecture

### Key Security Measures
1. **API Key Protection**
   - Stored encrypted in browser.storage
   - Never exposed in content scripts
   - Only used in background worker

2. **Content Security**
   - Strict CSP headers
   - Input sanitization
   - XSS prevention
   - No eval() usage

3. **Communication Security**
   - Message validation
   - Origin verification
   - Structured data only

### Threat Model
```
Threat              | Mitigation
--------------------|----------------------------------
Key exposure        | Encryption + isolated storage
XSS attacks         | CSP + sanitization
Data leakage        | Client-side only processing
MITM attacks        | HTTPS only for API calls
Malicious sites     | Permission model + origin checks
```

## Performance Optimization

### Bundle Size Optimization
1. **Code Splitting**
   - Separate bundles for popup/content/background
   - Lazy load non-critical features
   - Tree shaking for unused code

2. **Asset Optimization**
   - Minification and compression
   - Icon sprites
   - Efficient font loading

### Runtime Performance
1. **Caching Strategy**
   - LRU cache for API responses
   - Prefetch common queries
   - Background sync for updates

2. **Processing Optimization**
   - Web Workers for heavy tasks
   - Debounced user inputs
   - Virtual scrolling for results

## Browser Compatibility

### Manifest V3 Support
```json
{
  "manifest_version": 3,
  "name": "StrunzKnowledge MCP Client",
  "permissions": [
    "storage",
    "activeTab"
  ],
  "host_permissions": [
    "https://generativelanguage.googleapis.com/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"]
  }]
}
```

### Cross-Browser Considerations
1. **Chrome/Edge**: Full Manifest V3 support
2. **Firefox**: Partial V3 support, may need polyfills
3. **Safari**: Limited extension API, separate build needed

## Development Workflow

### Build Pipeline
```
Source Code
    ↓
TypeScript Compilation
    ↓
Bundling (Webpack/Rollup)
    ↓
Optimization
    ↓
Platform-specific builds
    ├─ Chrome/Edge
    ├─ Firefox
    └─ Safari
```

### Testing Strategy
1. Unit tests for core logic
2. Integration tests for API communication
3. E2E tests with Playwright
4. Manual testing on multiple browsers

## Future Enhancements

### Planned Features
1. **Offline Mode**: Local vector search capability
2. **Multi-LLM Support**: Beyond Gemini (Claude, GPT-4)
3. **Collaborative Features**: Share searches with team
4. **Advanced UI**: Floating assistant, voice input

### Scalability Considerations
1. **Modular Architecture**: Easy to add new features
2. **Plugin System**: Third-party integrations
3. **API Versioning**: Backward compatibility
4. **Progressive Web App**: Alternative deployment