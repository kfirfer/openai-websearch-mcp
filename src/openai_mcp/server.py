from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal, Optional, Annotated
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from openai import OpenAI, OpenAIError
from pydantic_extra_types.timezone_name import TimeZoneName
import os

mcp = MCPServer(
    name="OpenAI",
    instructions="This MCP server provides access to OpenAI's web search and brainstorming tools through the Model Context Protocol."
)

DEFAULT_MODELS = ["gpt-5.6-sol"]
DEFAULT_REASONING_MODELS = ["gpt-5.6-sol"]

ReasoningEffort = Literal["low", "medium", "high"]
SearchContextSize = Literal["low", "medium", "high"]

_EFFORT_LEVELS = ("low", "medium", "high")
_CONTEXT_SIZES = ("low", "medium", "high")

WEB_SEARCH_INSTRUCTIONS = (
    "Search the web thoroughly and provide comprehensive, well-sourced answers. "
    "Include relevant details, data points, and multiple perspectives where applicable. "
    "Always cite your sources with URLs."
)

ASK_INSTRUCTIONS = (
    "You are a brainstorming partner. Explore the idea from several angles before converging. "
    "Generate distinct options and, for each, state the trade-offs. "
    "Challenge assumptions, surface risks and open questions, and note anything the framing may be missing. "
    "Finish with a clear recommendation and the reasoning behind it."
)


def _get_models() -> list[str]:
    env = os.getenv("OPENAI_MODELS")
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    return DEFAULT_MODELS


def _get_reasoning_models() -> list[str]:
    env = os.getenv("OPENAI_REASONING_MODELS")
    if env is not None:
        return [m.strip() for m in env.split(",") if m.strip()]
    return DEFAULT_REASONING_MODELS


def _resolve_model(model: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Return (model, error). Exactly one of the two is set."""
    allowed = _get_models()
    if model is None:
        model = os.getenv("OPENAI_DEFAULT_MODEL", allowed[0])
    if model not in allowed:
        return None, f"Error: model '{model}' is not in the allowed models list: {allowed}"
    return model, None


def _env_choice(var: str, choices: tuple[str, ...]) -> Optional[str]:
    value = os.getenv(var)
    if value and value in choices:
        return value
    return None


def _reasoning_params(model: str, effort: Optional[str], default: str, env_var: str) -> dict:
    """Build the `reasoning` request block, or {} for non-reasoning models.

    Priority: env var override > per-request param > tool default.
    """
    if model not in _get_reasoning_models():
        return {}
    effort = _env_choice(env_var, _EFFORT_LEVELS) or effort or default
    return {"reasoning": {"effort": effort}}


def _web_search_tool(search_context_size: str, user_location: Optional["UserLocation"] = None) -> dict:
    tool = {"type": "web_search", "search_context_size": search_context_size}
    if user_location:
        tool["user_location"] = user_location.model_dump()
    return tool


def _create_response(**request_params) -> str:
    """Call the Responses API.

    API failures are re-raised as ToolError so the message reaches the model.
    The MCP SDK treats any other exception as a crash and hides its text.
    """
    client = OpenAI()
    try:
        response = client.responses.create(**request_params)
    except OpenAIError as exc:
        status = getattr(exc, "status_code", None)
        prefix = f"OpenAI API error {status}" if status else "OpenAI API error"
        raise ToolError(f"{prefix}: {exc}") from exc
    return response.output_text


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

Default model: gpt-5.6-sol (with reasoning support).
The result includes live web data with sourced citations.

Additional models can be enabled via the OPENAI_MODELS env var.""",
)
def openai_web_search(
    input: Annotated[str, Field(description="The search query or question to search for")],
    model: Annotated[Optional[str],
                     Field(description="AI model to use. Defaults to OPENAI_DEFAULT_MODEL env var or first allowed model")] = None,
    reasoning_effort: Annotated[Optional[ReasoningEffort],
                                Field(description="Reasoning effort level for supported models. Default: low")] = None,
    search_context_size: Annotated[SearchContextSize,
                                   Field(description="Amount of web context to retrieve: low (fast), medium (balanced), high (comprehensive)")] = "medium",
    user_location: Annotated[Optional[UserLocation],
                            Field(description="Optional user location for localized search results")] = None,
) -> str:
    model, error = _resolve_model(model)
    if error:
        return error

    search_context_size = _env_choice("OPENAI_SEARCH_CONTEXT_SIZE", _CONTEXT_SIZES) or search_context_size

    return _create_response(
        model=model,
        tools=[_web_search_tool(search_context_size, user_location)],
        input=input,
        instructions=WEB_SEARCH_INSTRUCTIONS,
        **_reasoning_params(model, reasoning_effort, default="low", env_var="OPENAI_REASONING_EFFORT"),
    )


@mcp.tool(
    name="openai_ask",
    description="""Brainstorm with an OpenAI reasoning model.

Use this to think through an idea, design, or problem: it explores several angles,
lays out distinct options with trade-offs, challenges assumptions, surfaces risks and
open questions, and ends with a recommendation.

Default model: gpt-5.6-sol with medium reasoning effort. Pass `context` for background
such as constraints, existing code, or prior findings.""",
)
def openai_ask(
    input: Annotated[str, Field(description="The idea, question, or problem to brainstorm")],
    context: Annotated[Optional[str],
                       Field(description="Optional background: constraints, existing code, prior findings")] = None,
    model: Annotated[Optional[str],
                     Field(description="AI model to use. Defaults to OPENAI_DEFAULT_MODEL env var or first allowed model")] = None,
    reasoning_effort: Annotated[Optional[ReasoningEffort],
                                Field(description="Reasoning effort level for supported models. Default: medium")] = None,
) -> str:
    model, error = _resolve_model(model)
    if error:
        return error

    if context:
        request_input = f"<context>\n{context}\n</context>\n\n{input}"
    else:
        request_input = input

    return _create_response(
        model=model,
        tools=[_web_search_tool("medium")],
        input=request_input,
        instructions=ASK_INSTRUCTIONS,
        **_reasoning_params(model, reasoning_effort, default="medium", env_var="OPENAI_ASK_REASONING_EFFORT"),
    )
