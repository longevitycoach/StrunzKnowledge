# Scripts Documentation

## Overview

All scripts are organized under `src/scripts/` with the following structure:
- `deployment/` - Server deployment scripts
- `testing/` - Testing and validation scripts
- `analysis/` - Content analysis tools
- `data/` - Data processing utilities

## Deployment Scripts

### main.py
**Location**: `/main.py`
**Purpose**: Main entry point that automatically selects the appropriate server based on environment
**Usage**: 
```bash
python main.py
```
**Environment Variables**:
- `RAILWAY_ENVIRONMENT`: Detects Railway deployment
- `RAILWAY_PUBLIC_DOMAIN`: Public domain (default: strunz.up.railway.app)
- `RAILWAY_PRIVATE_DOMAIN`: Private domain (default: strunz.railway.internal)

### railway_mcp_sse_server.py
**Location**: `src/scripts/deployment/railway_mcp_sse_server.py`
**Purpose**: Production Railway server with SSE endpoint for monitoring
**Features**:
- Health check endpoint at `/`
- SSE monitoring endpoint at `/sse`
- MCP protocol via stdio
**Usage**: Automatically selected when `RAILWAY_ENVIRONMENT=production`

### railway_mcp_server.py
**Location**: `src/scripts/deployment/railway_mcp_server.py`
**Purpose**: Minimal Railway server without SSE
**Features**:
- Health check only
- MCP protocol via stdio
**Usage**: For staging/development Railway deployments

### simple_server.py
**Location**: `src/scripts/deployment/simple_server.py`
**Purpose**: Lightweight health check server for testing
**Usage**: Fallback when MCP server fails to load

### start_server.py (REMOVED)
**Location**: `archive/deprecated-scripts/start_server.py`
**Purpose**: Legacy server starter
**Status**: Removed in cleanup - use `main.py` instead

## Testing Scripts

### test_sse_endpoint.sh
**Location**: `src/scripts/testing/test_sse_endpoint.sh`
**Purpose**: Test SSE endpoint functionality
**Usage**:
```bash
./test_sse_endpoint.sh [URL]
# Default: http://localhost:8000/sse
# Production: ./test_sse_endpoint.sh https://strunz.up.railway.app/sse
```

### test_mcp_jsonrpc.sh
**Location**: `src/scripts/testing/test_mcp_jsonrpc.sh`
**Purpose**: Comprehensive MCP tools testing via JSON-RPC
**Usage**:
```bash
./test_mcp_jsonrpc.sh
```
**Output**: `MCP_FULL_SERVER_TEST_REPORT.md`

### test_mcp_curl.sh (DEPRECATED)
**Location**: `src/scripts/testing/test_mcp_curl.sh`
**Purpose**: Legacy MCP testing script
**Status**: Deprecated - use `test_mcp_jsonrpc.sh`

### test_full_mcp_comprehensive.py
**Location**: `src/scripts/testing/test_full_mcp_comprehensive.py`
**Purpose**: Python-based comprehensive MCP testing
**Usage**:
```bash
python test_full_mcp_comprehensive.py
```
**Requirements**: `aiohttp`

### test_mcp_sse.py (DEPRECATED)
**Location**: `src/scripts/testing/test_mcp_sse.py`
**Purpose**: Legacy SSE testing
**Status**: Deprecated - use `test_sse_endpoint.sh`

## Analysis Scripts

### analyze_strunz_content.py
**Location**: `src/scripts/analysis/analyze_strunz_content.py`
**Purpose**: Analyze Dr. Strunz content structure and statistics
**Usage**:
```bash
python src/scripts/analysis/analyze_strunz_content.py
```
**Output**: Content analysis report with statistics

### refined_strunz_analysis.py
**Location**: `src/scripts/analysis/refined_strunz_analysis.py`
**Purpose**: Enhanced content analysis with topic modeling
**Usage**:
```bash
python src/scripts/analysis/refined_strunz_analysis.py
```
**Features**:
- Topic extraction
- Keyword analysis
- Content categorization

## Data Scripts

### reconstruct_indices.sh
**Location**: `src/scripts/data/reconstruct_indices.sh`
**Purpose**: Reconstruct FAISS indices from chunks during Docker build
**Usage**:
```bash
cd /app && bash src/scripts/data/reconstruct_indices.sh
```
**Note**: Used in Dockerfile for deployment

### split_faiss_index.py
**Location**: `src/scripts/data/split_faiss_index.py`
**Purpose**: Split large FAISS indices into <40MB chunks for GitHub
**Usage**:
```bash
python src/scripts/data/split_faiss_index.py data/faiss_indices/combined_index.faiss
```
**Output**: Multiple `.partXXX` files in `chunks/` directory

## Railway Deployment Workflow

1. **Local Development**:
   ```bash
   python main.py
   ```

2. **Docker Testing**:
   ```bash
   docker build -t strunz-mcp:test .
   docker run -p 8000:8000 strunz-mcp:test
   ./src/scripts/testing/test_sse_endpoint.sh
   ```

3. **Production Deployment**:
   - Push to main branch
   - Railway automatically builds and deploys
   - Test with: `./src/scripts/testing/test_sse_endpoint.sh https://strunz.up.railway.app/sse`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RAILWAY_PUBLIC_DOMAIN` | strunz.up.railway.app | Public domain for Railway |
| `RAILWAY_PRIVATE_DOMAIN` | strunz.railway.internal | Internal Railway domain |
| `RAILWAY_ENVIRONMENT` | - | Set to 'production' for prod |
| `PORT` | 8000 | Server port |
| `LOG_LEVEL` | INFO | Logging level |

## Cleanup Notes

The following scripts have been removed/deprecated:
- `start_server.py` - REMOVED, archived. Use `main.py` instead
- `official_mcp_server.py` - REMOVED, was duplicate of `mcp_sdk_clean.py`
- `test_mcp_curl.sh` - Use `test_mcp_jsonrpc.sh`
- `test_mcp_sse.py` - Use `test_sse_endpoint.sh`

All scripts now use consistent paths and the project structure follows:
```
StrunzKnowledge/
├── main.py                    # Main entry point
├── src/
│   ├── scripts/
│   │   ├── deployment/       # Server scripts
│   │   ├── testing/         # Test scripts
│   │   ├── analysis/        # Analysis tools
│   │   └── data/           # Data utilities
│   └── mcp/                # MCP server implementation
└── data/                   # Data files
```