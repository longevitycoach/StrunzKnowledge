# Claude Code MCP Setup Guide

## Overview

This guide documents the MCP (Model Context Protocol) servers configured for the StrunzKnowledge Claude Code project.

## Installed MCP Servers

### 1. Sequential Thinking Tools
- **Name**: `sequential-thinking`
- **Command**: `npx -y mcp-sequentialthinking-tools`
- **Purpose**: Helps break down complex problems into manageable steps
- **Usage**: Automatically available in Claude Code for systematic problem-solving

### 2. Context7
- **Name**: `context7`
- **Command**: `npx -y @upstash/context7-mcp`
- **Purpose**: Provides up-to-date, version-specific documentation
- **Usage**: Add "use context7" to your prompts for current documentation

### 3. StrunzKnowledge (Local)
- **Name**: `strunz-knowledge`
- **Command**: `python -m src.mcp.server`
- **Purpose**: Access to Dr. Strunz's comprehensive knowledge base
- **Features**: 19+ MCP tools for health, nutrition, and longevity insights

## Installation Commands

These MCP servers were installed using:
```bash
# Sequential Thinking
claude mcp add sequential-thinking -s user -- npx -y mcp-sequentialthinking-tools

# Context7
claude mcp add context7 -s user -- npx -y @upstash/context7-mcp

# StrunzKnowledge
claude mcp add strunz-knowledge -s user -- python -m src.mcp.server
```

## Managing MCP Servers

### List all MCP servers
```bash
claude mcp list
```

### Remove an MCP server
```bash
claude mcp remove <server-name>
```

### Add a new MCP server
```bash
claude mcp add <name> -s user -- <command> [args...]
```

## Usage Examples

### Using Sequential Thinking
When working on complex tasks, the sequential thinking tools will automatically help break down problems:
```
"I need to refactor the entire authentication system" 
# Sequential thinking will guide you through each step
```

### Using Context7
Append "use context7" to get current documentation:
```
"How do I create a Next.js 14 app router? use context7"
"Show me the latest React 18 hooks patterns. use context7"
```

### Using StrunzKnowledge
Access Dr. Strunz's health knowledge:
```
"Search for vitamin D recommendations"
"Create a longevity protocol for a 45-year-old"
```

## Troubleshooting

### If MCP servers don't appear:
1. Restart Claude Code
2. Check with `claude mcp list`
3. Ensure Node.js is installed (for npx commands)
4. For StrunzKnowledge, ensure you're in the project directory

### To test MCP servers:
```bash
# Test if they're responsive
claude mcp serve
```

## Environment Setup

For the StrunzKnowledge MCP to work properly:
1. Ensure you're in the `/Users/ma3u/projects/StrunzKnowledge` directory
2. Python environment should have all dependencies installed
3. FAISS indices should be available in `data/faiss_indices/`

## Additional Configuration

The full MCP configuration is stored in:
- **User config**: `~/.claude.json` (or Claude Code's config location)
- **Project config**: `claude_code_config.json` (in project root)

## Benefits

With these MCP servers, you can:
1. **Sequential Thinking**: Systematically approach complex coding tasks
2. **Context7**: Always get the latest API documentation and avoid outdated code
3. **StrunzKnowledge**: Access comprehensive health and nutrition information

These tools work together to enhance your Claude Code experience with better problem-solving, current documentation, and domain-specific knowledge.