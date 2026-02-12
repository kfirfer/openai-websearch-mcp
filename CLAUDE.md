# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An MCP (Model Context Protocol) server that exposes OpenAI's web search with reasoning models as a tool for AI assistants (Claude Desktop, Cursor, Claude Code). Single tool: `openai_web_search`.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the MCP server locally
uv run python -m openai_websearch_mcp

# Debug with MCP Inspector
npx @modelcontextprotocol/inspector uvx openai-websearch-mcp
```

No test suite or linter is configured.

## Architecture

The codebase is minimal — four Python modules under `src/openai_websearch_mcp/`:

- **server.py** — Core logic. Defines a single `@mcp.tool()` function `openai_web_search()` that builds an OpenAI API request with web search tool parameters and returns `response.output_text`. Handles model-specific reasoning effort defaults (low for gpt-5-mini, medium for others). Only adds `reasoning` params for models in the `reasoning_models` list.
- **cli.py** — Typer CLI for automated installation into Claude Desktop. Validates API keys against OpenAI's API, detects config paths cross-platform, and writes `claude_desktop_config.json`.
- **__init__.py** — Exports `main()` which starts the FastMCP server via `mcp.run()`.
- **__main__.py** — Module entry point (`python -m` support).

## Key Details

- **Package manager**: uv (with `uv.lock`). Build backend: hatchling.
- **Python**: >=3.10
- **Entry points** (defined in `pyproject.toml`): `openai-websearch-mcp` (server), `openai-websearch-mcp-install` (CLI installer)
- **Environment variables**: `OPENAI_API_KEY` (required), `OPENAI_DEFAULT_MODEL` (optional, defaults to `gpt-5-mini`)
- **Supported models**: gpt-4o, gpt-4o-mini (no reasoning); gpt-5, gpt-5-mini, gpt-5-nano, o3, o4-mini (with reasoning)
- **Pydantic v2** is used for data models — `UserLocation` uses `TimeZoneName` from `pydantic_extra_types`
