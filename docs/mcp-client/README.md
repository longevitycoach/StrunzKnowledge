# MCP Client Documentation

## Overview
The StrunzKnowledge MCP Client is a browser extension that enables seamless integration of Dr. Strunz's knowledge base into any website using the Model Context Protocol (MCP).

## Key Features
- **Auth-less Integration**: Works with just a Gemini Key - no OAuth or API keys required
- **Universal Compatibility**: Functions on any website through browser extension
- **Privacy-First**: All processing happens client-side
- **Cross-Browser Support**: Chrome, Firefox, and Edge compatibility

## Documentation Structure

### 1. [Architecture Overview](./architecture.md)
Technical architecture and design decisions for the MCP client implementation.

### 2. [SDK Evaluation Framework](./sdk-evaluation.md)
Comprehensive evaluation of TypeScript, Python, Go, and Rust SDKs for browser extension development.

### 3. [Implementation Guide](./implementation-guide.md)
Step-by-step guide for implementing the MCP client browser extension.

### 4. [API Reference](./api-reference.md)
Complete API documentation for the MCP client SDK.

### 5. [Security Guide](./security.md)
Security considerations and best practices for client-side processing.

### 6. [User Guide](./user-guide.md)
End-user documentation for installing and using the browser extension.

## Quick Start

### Prerequisites
- Modern web browser (Chrome 90+, Firefox 88+, Edge 90+)
- Gemini API Key from Google AI Studio

### Installation
1. Download the extension from the browser store
2. Click the extension icon in your browser toolbar
3. Enter your Gemini API Key
4. Start using Dr. Strunz's knowledge on any website!

### Basic Usage
```javascript
// Example: Searching for nutrition information
const client = new MCPClient({
  geminiKey: 'your-key-here'
});

const results = await client.search('vitamin d benefits');
console.log(results);
```

## Development Status

### Current Phase: SDK Evaluation (Story-001)
- Evaluating TypeScript, Python, Go, and Rust options
- Focus on auth-less integration capabilities
- Bundle size optimization for browser extension

### Upcoming Milestones
1. **Q1 2025**: SDK selection and POC implementation
2. **Q2 2025**: Browser extension MVP
3. **Q3 2025**: Multi-browser support
4. **Q4 2025**: Production release

## Contributing
See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on contributing to the MCP client development.

## Support
- GitHub Issues: [Report bugs or request features](https://github.com/longevitycoach/StrunzKnowledge/issues)
- Documentation: [Full documentation](https://github.com/longevitycoach/StrunzKnowledge/tree/main/docs)

## License
MIT License - see [LICENSE](../../LICENSE) for details.