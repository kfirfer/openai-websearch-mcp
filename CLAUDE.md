# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An MCP (Model Context Protocol) server that exposes OpenAI's web search with reasoning models as tools for AI assistants (Claude Desktop, Cursor, Claude Code). Two tools: `openai_web_search` (live web search) and `openai_ask` (brainstorming).

## Development Commands

```bash
# Install dependencies
uv sync

# Run the MCP server locally
uv run python -m openai_mcp

# Debug with MCP Inspector
npx @modelcontextprotocol/inspector uvx openai-mcp
```

Tests: `uv run pytest` (pytest, in `tests/`; mocks the OpenAI client). No linter is configured.

## Architecture

The codebase is minimal — four Python modules under `src/openai_mcp/`:

- **server.py** — Core logic. Defines two `@mcp.tool()` functions that call the Responses API (`client.responses.create()`) and return `response.output_text`: `openai_web_search()` (web search, default effort `low`) and `openai_ask()` (brainstorming, default effort `medium`, optional `context` param, web search attached but the model decides whether to use it). Shared helpers handle model allowlisting (`_resolve_model`), reasoning params (`_reasoning_params`, priority: env var > request param > tool default; only for models in the reasoning models list), and the API call (`_create_response`).
- **cli.py** — Typer CLI for automated installation into Claude Desktop. Validates API keys against OpenAI's API, detects config paths cross-platform, and writes `claude_desktop_config.json`.
- **__init__.py** — Exports `main()` which starts the MCPServer via `mcp.run()`.
- **__main__.py** — Module entry point (`python -m` support).

## Key Details

- **Package manager**: uv (with `uv.lock`). Build backend: hatchling.
- **Python**: >=3.10
- **API**: OpenAI Responses API (`client.responses.create()`) with `web_search` tool (GA)
- **Entry points** (defined in `pyproject.toml`): `openai-mcp` (server), `openai-mcp-install` (CLI installer)
- **Environment variables**: `OPENAI_API_KEY` (required), `OPENAI_DEFAULT_MODEL` (optional, defaults to `gpt-5.6-sol`), `OPENAI_MODELS` (optional, comma-separated allowed models), `OPENAI_REASONING_MODELS` (optional, comma-separated reasoning models), `OPENAI_REASONING_EFFORT` (optional, overrides reasoning effort for `openai_web_search`), `OPENAI_ASK_REASONING_EFFORT` (optional, overrides reasoning effort for `openai_ask`), `OPENAI_SEARCH_CONTEXT_SIZE` (optional, overrides search context size for all requests)
- **Default model**: gpt-5.6-sol (with reasoning). Additional models can be enabled via `OPENAI_MODELS` and `OPENAI_REASONING_MODELS` env vars.
- **Pydantic v2** is used for data models — `UserLocation` uses `TimeZoneName` from `pydantic_extra_types`
