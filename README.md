# OpenAI WebSearch MCP Server 🔍

[![PyPI version](https://badge.fury.io/py/openai-websearch-mcp.svg)](https://badge.fury.io/py/openai-websearch-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced MCP server that provides intelligent web search capabilities using OpenAI's reasoning models. Perfect for AI assistants that need up-to-date information with smart reasoning capabilities.

## ✨ Features

- **🧠 Reasoning Model Support**: Full compatibility with OpenAI's latest reasoning models (gpt-5, gpt-5-mini, gpt-5-nano, o3, o4-mini)
- **⚡ Smart Effort Control**: Intelligent `reasoning_effort` defaults based on use case
- **🔄 Multi-Mode Search**: Fast iterations with gpt-5-mini or deep research with gpt-5
- **🌍 Localized Results**: Support for location-based search customization
- **🔗 Live Web Search**: Real-time web data with sourced citations via OpenAI's `web_search` tool
- **🔧 Flexible Configuration**: Environment variable support for easy deployment

## 🚀 Quick Start

### One-Click Installation for Claude Desktop

```bash
OPENAI_API_KEY=sk-xxxx uvx --with openai-websearch-mcp openai-websearch-mcp-install
```

Replace `sk-xxxx` with your OpenAI API key from the [OpenAI Platform](https://platform.openai.com/).

## ⚙️ Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openai-websearch-mcp": {
      "command": "uvx",
      "args": ["openai-websearch-mcp"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here",
        "OPENAI_DEFAULT_MODEL": "gpt-5-mini"
      }
    }
  }
}
```

### Cursor

Add to your MCP settings in Cursor:

1. Open Cursor Settings (`Cmd/Ctrl + ,`)
2. Search for "MCP" or go to Extensions → MCP
3. Add server configuration:

```json
{
  "mcpServers": {
    "openai-websearch-mcp": {
      "command": "uvx",
      "args": ["openai-websearch-mcp"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here",
        "OPENAI_DEFAULT_MODEL": "gpt-5-mini"
      }
    }
  }
}
```

### Claude Code

Claude Code automatically detects MCP servers configured for Claude Desktop. Use the same configuration as above for Claude Desktop.

### Local Development

For local testing, use the absolute path to your virtual environment:

```json
{
  "mcpServers": {
    "openai-websearch-mcp": {
      "command": "/path/to/your/project/.venv/bin/python",
      "args": ["-m", "openai_websearch_mcp"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here",
        "OPENAI_DEFAULT_MODEL": "gpt-5-mini",
        "PYTHONPATH": "/path/to/your/project/src"
      }
    }
  }
}
```

## 🛠️ Available Tools

### `openai_web_search`

Intelligent web search with reasoning model support.

#### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `input` | `string` | The search query or question to search for | *Required* |
| `model` | `string` | AI model to use. Supports gpt-4o, gpt-4o-mini, gpt-5, gpt-5-mini, gpt-5-nano, o3, o4-mini | `gpt-4o` (or `OPENAI_DEFAULT_MODEL`) |
| `reasoning_effort` | `string` | Reasoning effort level: low, medium, high, minimal | Smart default |
| `search_context_size` | `string` | Web context amount: low, medium, high | `medium` |
| `user_location` | `object` | Optional location for localized results | `null` |

## 💬 Usage Examples

Once configured, simply ask your AI assistant to search for information using natural language:

### Quick Search
> "Search for the latest developments in AI reasoning models using openai_web_search"

### Deep Research
> "Use openai_web_search with gpt-5 and high reasoning effort to provide a comprehensive analysis of quantum computing breakthroughs"

### Localized Search
> "Search for local tech meetups in San Francisco this week using openai_web_search"

The AI assistant will automatically use the `openai_web_search` tool with appropriate parameters based on your request.

## 🤖 Model Selection Guide

### Quick Multi-Round Searches 🚀
- **Recommended**: `gpt-5-mini` with `reasoning_effort: "low"`
- **Use Case**: Fast iterations, real-time information, multiple quick queries
- **Benefits**: Lower latency, cost-effective for frequent searches

### Deep Research 🔬
- **Recommended**: `gpt-5` with `reasoning_effort: "medium"` or `"high"`
- **Use Case**: Comprehensive analysis, complex topics, detailed investigation
- **Benefits**: Multi-round reasoned results, no need for agent iterations

### Model Comparison

| Model | Reasoning | Default Effort | Best For |
|-------|-----------|----------------|----------|
| `gpt-4o` | ❌ | N/A | Standard search |
| `gpt-4o-mini` | ❌ | N/A | Basic queries |
| `gpt-5-mini` | ✅ | `low` | Fast iterations |
| `gpt-5` | ✅ | `medium` | Deep research |
| `gpt-5-nano` | ✅ | `medium` | Balanced approach |
| `o3` | ✅ | `medium` | Advanced reasoning |
| `o4-mini` | ✅ | `medium` | Efficient reasoning |

## 📦 Installation

### Using uvx (Recommended)

```bash
# Install and run directly
uvx openai-websearch-mcp

# Or install globally
uvx install openai-websearch-mcp
```

### Using pip

```bash
# Install from PyPI
pip install openai-websearch-mcp

# Run the server
python -m openai_websearch_mcp
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/openai-websearch-mcp.git
cd openai-websearch-mcp

# Install dependencies
uv sync

# Run in development mode
uv run python -m openai_websearch_mcp
```

## 👩‍💻 Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/openai-websearch-mcp.git
cd openai-websearch-mcp

# Create virtual environment and install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | *Required* |
| `OPENAI_DEFAULT_MODEL` | Default model to use | First allowed model (`gpt-4o`) |
| `OPENAI_MODELS` | Comma-separated list of allowed models | See DEFAULT_MODELS |
| `OPENAI_REASONING_MODELS` | Comma-separated list of reasoning models | See DEFAULT_REASONING_MODELS |

## 🐛 Debugging

### Using MCP Inspector

```bash
# For uvx installations
npx @modelcontextprotocol/inspector uvx openai-websearch-mcp

# For pip installations
npx @modelcontextprotocol/inspector python -m openai_websearch_mcp
```

### Common Issues

**Issue**: "Unsupported parameter: 'reasoning.effort'"
**Solution**: This occurs when using non-reasoning models (gpt-4o, gpt-4o-mini) with reasoning_effort parameter. The server automatically handles this by only applying reasoning parameters to compatible models.

**Issue**: "No module named 'openai_websearch_mcp'"
**Solution**: Ensure you've installed the package correctly and your Python path includes the package location.

## 🔄 Changelog

### v0.5.0

- **Upgraded to GA `web_search` tool** — replaces `web_search_preview` with the generally available `web_search` tool in the Responses API
- **Removed `type` parameter** — no longer needed since we use the GA `web_search` tool
- **Cleaned up imports** — removed duplicate imports, added `from __future__ import annotations`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- 🤖 Generated with [Claude Code](https://claude.ai/code)
- 🔥 Powered by [OpenAI's Web Search API](https://openai.com)
- 🛠️ Built on the [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Co-Authored-By**: Claude <noreply@anthropic.com>
