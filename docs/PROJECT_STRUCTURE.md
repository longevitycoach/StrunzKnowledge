# StrunzKnowledge Project Structure

Clean, organized structure following MCP standards.

## 📁 Directory Structure

```
StrunzKnowledge/
├── data/                      # All data files
│   ├── raw/                   # Raw HTML files for processing
│   │   ├── forum/             # Forum HTML files (wget output)
│   │   │   ├── fitness/       # 1,310 files
│   │   │   ├── ernaehrung/    # 323 files
│   │   │   ├── gesundheit/    # 329 files
│   │   │   ├── bluttuning/    # 363 files
│   │   │   ├── mental/        # 351 files
│   │   │   └── infektion-und-praevention/ # 312 files
│   │   ├── news/              # 467+ news HTML files with archives
│   │   └── robots.txt         # Site robots.txt
│   ├── processed/             # Processed data (Docling output)
│   ├── analysis/              # Analysis reports
│   ├── delta/                 # Delta packages for incremental updates
│   └── update_metadata.json   # Forum update tracking metadata
├── src/                       # All source code
│   ├── scraper/               # Core scraping modules
│   ├── rag/                   # Docling and vector processing
│   ├── mcp/                   # MCP server implementation
│   ├── scripts/               # Management scripts
│   ├── analysis/              # Analysis modules
│   ├── tests/                 # Test files
│   └── tools/                 # Utility scripts and tools
├── logs/                      # Log files (git-ignored)
│   ├── *_download.log         # wget download logs
│   ├── scraping.log           # Scraping logs
│   └── README.md              # Log documentation
├── docs/                      # Documentation
├── archive/                   # Archived legacy scripts
├── config/                    # Configuration files
├── venv/                      # Python virtual environment
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── CLAUDE.md                  # Claude-specific instructions
├── LICENSE                    # MIT License
└── .gitignore                 # Git ignore rules

## 🔒 Git-Ignored Files

The following are excluded from version control:
- `/logs/` - All log files
- `*.log` - Any log file
- `/data/raw/` - Raw scraped data
- `/data/processed/` - Processed data
- `/venv/` - Virtual environment
- `*.pkl`, `*.faiss` - Binary data files

## 🛠️ Key Scripts

### Main Entry Point
- `main.py` - MCP-compliant main entry with commands

### Core Modules (src/)
- `scraper/` - Web scraping implementations
- `rag/` - Docling OCR and vector store
- `mcp/` - Model Context Protocol server

### Utility Tools (src/tools/)
- `wget_forum_downloader.py` - Forum download manager
- `forum_download_summary.py` - Analyze downloaded content
- `monitor_downloads.sh` - Monitor active downloads
- `analyze_wget_downloads.py` - Analyze wget results
- `forum_update_tracker.py` - Track changes and manage delta updates
- `init_forum_baseline.py` - Initialize baseline for tracking

## 📊 Current Data Status

- **Forum HTML Files:** 2,988 files across 6 categories
- **News HTML Files:** 467+ articles including archives
- **Total Content:** 3,455+ HTML files
- **Total Size:** ~300MB of raw content
- **Last Update:** July 11, 2025 at 19:40
- **Update Tracking:** Enabled with SHA256 hashing
- **Status:** Ready for Docling processing

## 🚀 Next Steps

1. **Process with Docling:** Convert HTML to structured text
2. **Build Vector Database:** Create FAISS index
3. **Deploy MCP Server:** Enable AI-powered search
4. **Test Integration:** Verify semantic search works

## 🔧 Maintenance

### Clean Logs
```bash
find logs/ -name "*.log" -mtime +7 -delete
```

### Monitor Downloads
```bash
./src/tools/monitor_downloads.sh
```

### Check Data Status
```bash
python src/tools/forum_download_summary.py
```