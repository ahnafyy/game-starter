import pytest

import agents
from agents.shared.base_agent import BaseAgent

ALL_AGENT_CLASSES = [
    agents.GameDirectorAgent,
    agents.GameplayEngineerAgent,
    agents.LevelDesignerAgent,
    agents.NpcBehaviorAgent,
    agents.QaPlaytestAgent,
    agents.AssetPipelineAgent,
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


@pytest.mark.parametrize("agent_class", ALL_AGENT_CLASSES)
async def test_agent_run_raises_not_implemented(agent_class):
    from agents.shared.contracts import AgentTask

    instance = agent_class()
    task = AgentTask(description="smoke test")
    with pytest.raises(NotImplementedError):
        await instance.run(task)
