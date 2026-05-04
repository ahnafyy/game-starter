from agents.shared.contracts import AgentResult, AgentTask, MCPCommand, MCPResponse


def test_mcp_command_defaults():
    cmd = MCPCommand(type="get_scene_info")
    assert cmd.params == {}


def test_mcp_response_error_is_optional():
    resp = MCPResponse(status="ok", result={"actors": []})
    assert resp.error is None


def test_agent_task_defaults():
    task = AgentTask(description="Place a cube")
    assert task.context == {}
    assert task.priority == 1


def test_agent_task_priority_bounds():
    task = AgentTask(description="test", priority=5)
    assert task.priority == 5


def test_agent_result_round_trip():
    task = AgentTask(description="test")
    cmd = MCPCommand(type="create_object", params={"name": "Cube"})
    result = AgentResult(
        agent="level-designer",
        task=task,
        status="completed",
        output={"actors_placed": ["Cube"]},
        mcp_commands_issued=[cmd],
    )
    dumped = result.model_dump()
    assert dumped["agent"] == "level-designer"
    assert len(dumped["mcp_commands_issued"]) == 1
