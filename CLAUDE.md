# Dr. Strunz Knowledge Base - Claude Code Development Guide

## Content Sources

### 1. Books (13 total)
The following Dr. Ulrich Strunz books have been processed:

| Title | Year | Filename |
|-------|------|----------|
| Fitness drinks | 2002 | Dr.Ulrich-Strunz_Fitness_drinks_2002.pdf |
| Die neue Diaet Das Fitnessbuch | 2010 | Dr.Ulrich-Strunz_Die_neue_Diaet_Das_Fitnessbuch_2010.pdf |
| Das Geheimnis der Gesundheit | 2010 | Dr.Ulrich-Strunz_Das_Geheimnis_der_Gesundheit_2010.pdf |
| Das neue Anti-Krebs-Programm - dem Krebs keine Chance geben  | 2012 | Dr.Ulrich-Strunz_Das_neue_Anti-Krebs-Programm_-_dem_Krebs_keine_Chance_geben__2012.pdf |
| No-Carb-Smoothies | 2015 | Dr.Ulrich-Strunz_No-Carb-Smoothies_2015.pdf |
| Wunder der Heilung | 2015 | Dr.Ulrich-Strunz_Wunder_der_Heilung_2015.pdf |
| Blut - Die Geheimnisse Unseres flussigen Organs | 2016 | Dr.Ulrich-Strunz_Blut_-_Die_Geheimnisse_Unseres_flussigen_Organs_2016.pdf |
| Das Strunz-Low-Carb-Kochbuch | 2016 | Dr.Ulrich-Strunz_Das_Strunz-Low-Carb-Kochbuch_2016.pdf |
| Heilung erfahren | 2019 | Dr.Ulrich-Strunz_Heilung_erfahren_2019.pdf |
| 77 Tipps fuer Ruecken und Gelenke | 2021 | Dr.Ulrich-Strunz_77_Tipps_fuer_Ruecken_und_Gelenke_2021.pdf |
| Das Stress-weg-Buch | 2022 | Dr.Ulrich-Strunz_Das_Stress-weg-Buch_2022.pdf |
| Die Amino-Revolution | 2022 | Dr.Ulrich-Strunz_Die_Amino-Revolution_2022.pdf |
| Der Gen-Trick | 2025 | Dr.Ulrich-Strunz_Der_Gen-Trick_2025.pdf |

### 2. News Articles
- **Total articles**: 6,953 unique articles
- **Date range**: 2004-09-28 to 2025-07-11
- **Base URL**: https://www.strunz.com/news/
- **URL pattern**: https://www.strunz.com/news/[article-slug].html

### 3. Forum Content
- **Total chunks**: 6,400
- **Status**: Limited data available (only showing date 02.05.2020)
- **Note**: Forum scraping appears incomplete and may need to be redone

## Technical Decisions

### MCP Protocol Implementation
- **Decision**: Use FastMCP + MCP inspector for robust MCP client
- **Repository**: https://github.com/evalstate/fast-agent
- **Key Features**:
  - Full MCP protocol support
  - Robust agent implementation
  - Detailed documentation in project README

### MCP Transport Strategy (2025-01-15)

**Decision**: Use FastMCP with SSE transport for production deployment

**Rationale**:
1. **FastMCP supports multiple transports**: stdio (local), HTTP, and SSE
2. **SSE is recommended for remote servers**: Better for Claude Desktop integration
3. **HTTP transport is deprecated**: Moving to Streamable HTTP as per MCP spec
4. **OAuth 2.1 support**: Required for Claude Desktop authentication

**Implementation**:
```python
# Production (Railway)
mcp.run(transport="sse", host="0.0.0.0", port=PORT)

# Local development
mcp.run()  # Uses stdio by default
```

### Testing Strategy

**Decision**: Use MCP Inspector + Fast Agent for comprehensive testing

**Tools**:
1. **MCP Inspector**: Protocol-level debugging and validation
2. **Fast Agent**: Robust MCP client with full protocol support
3. **Local test servers**: For HTTP/SSE transport testing

**Test Coverage**:
- Protocol compliance (JSON-RPC 2.0)
- Transport functionality (stdio, HTTP, SSE)
- Tool execution and response formatting
- Authentication flow (OAuth for SSE)

### Authentication Architecture

**Current Status**: Placeholder implementation
- Demo token endpoint for testing
- No real OAuth implementation yet

**Future Requirements** (for Claude Desktop):
1. Dynamic Client Registration
2. OAuth 2.1 authorization flow
3. Bearer token validation
4. Session management for SSE

### FastMCP vs Official MCP SDK

**Decision**: Use FastMCP for production

**Comparison**:
| Feature | FastMCP | Official MCP SDK |
|---------|---------|------------------|
| Transport Support | stdio, HTTP, SSE | stdio, SSE, Streamable HTTP |
| Ease of Use | Simple decorators | More complex setup |
| Production Ready | Yes | Yes |
| OAuth Support | Built-in | Requires implementation |
| Documentation | Good | Comprehensive |

**Rationale**: FastMCP provides simpler implementation with all required features for our use case.

[Rest of the existing content remains unchanged...]