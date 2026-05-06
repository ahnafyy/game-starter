import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import agents
from agents.shared.base_agent import BaseAgent
from agents.shared.contracts import MCPResponse

ALL_AGENT_CLASSES = [
    agents.GameDirectorAgent,
    agents.GameplayEngineerAgent,
    agents.LevelDesignerAgent,
    agents.NpcBehaviorAgent,
    agents.QaPlaytestAgent,
    agents.AssetPipelineAgent,
]

STUB_AGENT_CLASSES = [
    agents.GameDirectorAgent,
    agents.GameplayEngineerAgent,
    agents.LevelDesignerAgent,
    agents.NpcBehaviorAgent,
    agents.QaPlaytestAgent,
]


@pytest.mark.parametrize("agent_class", ALL_AGENT_CLASSES)
def test_agent_instantiates(agent_class):
    instance = agent_class()
    assert isinstance(instance, BaseAgent)
    assert instance.role != ""


@pytest.mark.parametrize("agent_class", ALL_AGENT_CLASSES)
def test_agent_has_system_prompt(agent_class):
    instance = agent_class()
    assert len(instance._system_prompt) > 50


@pytest.mark.parametrize("agent_class", ALL_AGENT_CLASSES)
def test_agent_config_has_required_keys(agent_class):
    instance = agent_class()
    assert "role" in instance._config
    assert "model" in instance._config
    assert "allowed_tools" in instance._config


@pytest.mark.parametrize("agent_class", STUB_AGENT_CLASSES)
async def test_agent_run_raises_not_implemented(agent_class):
    from agents.shared.contracts import AgentTask

    instance = agent_class()
    task = AgentTask(description="smoke test")
    with pytest.raises(NotImplementedError):
        await instance.run(task)


async def test_asset_pipeline_agent_run_completed(monkeypatch):
    """AssetPipelineAgent.run() returns a completed AgentResult when LLM + MCP succeed."""
    from agents.shared.contracts import AgentTask

    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")

    llm_payload = json.dumps({"python_snippet": "print('ok')", "reasoning": "test"})
    mock_choice = MagicMock()
    mock_choice.message.content = llm_payload
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [mock_choice]

    mock_mcp_response = MCPResponse(status="ok", result={"assets_validated": 0})

    with (
        patch("agents.roles.asset_pipeline.agent.OpenAI") as mock_openai_cls,
        patch("agents.roles.asset_pipeline.agent.MCPClient") as mock_mcp_cls,
    ):
        mock_openai_cls.return_value.chat.completions.create.return_value = mock_llm_response

        mock_mcp_instance = AsyncMock()
        mock_mcp_instance.send_command = AsyncMock(return_value=mock_mcp_response)
        mock_mcp_instance.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp_instance.__aexit__ = AsyncMock(return_value=False)
        mock_mcp_cls.return_value = mock_mcp_instance

        agent = agents.AssetPipelineAgent()
        result = await agent.run(AgentTask(description="validate asset names"))

    assert result.status == "completed"
    assert result.agent == "asset_pipeline"
    assert len(result.mcp_commands_issued) == 1
    assert result.mcp_commands_issued[0].type == "execute_python"


async def test_asset_pipeline_agent_run_blocked_on_mcp_error(monkeypatch):
    """AssetPipelineAgent.run() returns blocked when MCP returns an error."""
    from agents.shared.contracts import AgentTask

    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")

    llm_payload = json.dumps({"python_snippet": "bad_code()", "reasoning": "test"})
    mock_choice = MagicMock()
    mock_choice.message.content = llm_payload
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [mock_choice]

    mock_mcp_response = MCPResponse(status="error", error="SyntaxError in script")

    with (
        patch("agents.roles.asset_pipeline.agent.OpenAI") as mock_openai_cls,
        patch("agents.roles.asset_pipeline.agent.MCPClient") as mock_mcp_cls,
    ):
        mock_openai_cls.return_value.chat.completions.create.return_value = mock_llm_response

        mock_mcp_instance = AsyncMock()
        mock_mcp_instance.send_command = AsyncMock(return_value=mock_mcp_response)
        mock_mcp_instance.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp_instance.__aexit__ = AsyncMock(return_value=False)
        mock_mcp_cls.return_value = mock_mcp_instance

        agent = agents.AssetPipelineAgent()
        result = await agent.run(AgentTask(description="validate asset names"))

    assert result.status == "blocked"
    assert result.error == "SyntaxError in script"
