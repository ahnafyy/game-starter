from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MCPCommand(BaseModel):
    """A command sent to the Unreal MCP TCP server."""

    type: str
    params: dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """A response from the Unreal MCP TCP server."""

    status: str
    result: Any = None
    error: str | None = None


class AgentTask(BaseModel):
    """A task handed to an agent."""

    description: str
    context: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)


class AgentResult(BaseModel):
    """The result produced by an agent after executing a task."""

    agent: str
    task: AgentTask
    status: str
    output: Any = None
    mcp_commands_issued: list[MCPCommand] = Field(default_factory=list)
    error: str | None = None
