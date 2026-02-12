from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal, Optional, Annotated
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from pydantic_extra_types.timezone_name import TimeZoneName
import os

mcp = FastMCP(
    name="OpenAI Web Search",
    instructions="This MCP server provides access to OpenAI's web search functionality through the Model Context Protocol."
)

DEFAULT_MODELS = ["gpt-5.2"]
DEFAULT_REASONING_MODELS = ["gpt-5.2"]


def _get_models() -> list[str]:
    env = os.getenv("OPENAI_MODELS")
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    return DEFAULT_MODELS


def _get_reasoning_models() -> list[str]:
    env = os.getenv("OPENAI_REASONING_MODELS")
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    return DEFAULT_REASONING_MODELS


class UserLocation(BaseModel):
    type: Literal["approximate"] = "approximate"
    city: str
    country: str = None
    region: str = None
    timezone: TimeZoneName


@mcp.tool(
    name="openai_web_search",
    description="""OpenAI Web Search with reasoning models.

Searches the web for real-time information using OpenAI's web search tool.

Default model: gpt-5.2 (with reasoning support).
The result includes live web data with sourced citations.

Additional models can be enabled via the OPENAI_MODELS env var.""",
)
def openai_web_search(
    input: Annotated[str, Field(description="The search query or question to search for")],
    model: Annotated[Optional[str],
                     Field(description="AI model to use. Defaults to OPENAI_DEFAULT_MODEL env var or first allowed model")] = None,
    reasoning_effort: Annotated[Optional[Literal["low", "medium", "high"]],
                                Field(description="Reasoning effort level for supported models. Default: low")] = None,
    search_context_size: Annotated[Literal["low", "medium", "high"],
                                   Field(description="Amount of web context to retrieve: low (fast), medium (balanced), high (comprehensive)")] = "medium",
    user_location: Annotated[Optional[UserLocation],
                            Field(description="Optional user location for localized search results")] = None,
) -> str:
    if model is None:
        allowed = _get_models()
        model = os.getenv("OPENAI_DEFAULT_MODEL", allowed[0])

    allowed_models = _get_models()
    if model not in allowed_models:
        return f"Error: model '{model}' is not in the allowed models list: {allowed_models}"

    client = OpenAI()
    reasoning_models = _get_reasoning_models()

    # Env var overrides for search_context_size and reasoning_effort
    env_context_size = os.getenv("OPENAI_SEARCH_CONTEXT_SIZE")
    if env_context_size and env_context_size in ("low", "medium", "high"):
        search_context_size = env_context_size

    env_reasoning = os.getenv("OPENAI_REASONING_EFFORT")
    if env_reasoning and env_reasoning in ("low", "medium", "high"):
        reasoning_effort = env_reasoning

    # Build web search tool
    tool = {
        "type": "web_search",
        "search_context_size": search_context_size,
    }
    if user_location:
        tool["user_location"] = user_location.model_dump()

    # Build request params
    request_params = {
        "model": model,
        "tools": [tool],
        "input": input,
        "instructions": "Search the web thoroughly and provide comprehensive, well-sourced answers. "
                        "Include relevant details, data points, and multiple perspectives where applicable. "
                        "Always cite your sources with URLs.",
    }

    # Set reasoning effort for reasoning models
    # Priority: env var override > per-request param > per-model default
    if model in reasoning_models:
        if reasoning_effort is None:
            reasoning_effort = "low"
        request_params["reasoning"] = {"effort": reasoning_effort}

    response = client.responses.create(**request_params)
    return response.output_text
