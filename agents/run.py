from __future__ import annotations

import asyncio
import importlib
import json
from pathlib import Path

import click
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from agents.shared.contracts import AgentTask

AGENT_REGISTRY: dict[str, str] = {
    "game-director": "agents.roles.game_director.agent",
    "gameplay-engineer": "agents.roles.gameplay_engineer.agent",
    "level-designer": "agents.roles.level_designer.agent",
    "npc-behavior": "agents.roles.npc_behavior.agent",
    "qa-playtest": "agents.roles.qa_playtest.agent",
    "asset-pipeline": "agents.roles.asset_pipeline.agent",
}


def _load_agent(name: str):
    module_path = AGENT_REGISTRY[name]
    module = importlib.import_module(module_path)
    agent_class = next(
        cls
        for attr, cls in vars(module).items()
        if isinstance(cls, type) and attr.endswith("Agent") and attr != "BaseAgent"
    )
    return agent_class()


@click.command()
@click.option(
    "--agent",
    required=True,
    type=click.Choice(list(AGENT_REGISTRY.keys())),
    help="Which agent to run.",
)
@click.option("--task", required=True, help="Task description for the agent.")
@click.option(
    "--context",
    default="{}",
    show_default=True,
    help="JSON object with additional task context.",
)
def main(agent: str, task: str, context: str) -> None:
    """Run a dev-workflow agent against the GameStarter Unreal project."""
    try:
        ctx = json.loads(context)
    except json.JSONDecodeError as exc:
        raise click.BadParameter(f"--context must be valid JSON: {exc}") from exc

    instance = _load_agent(agent)
    task_obj = AgentTask(description=task, context=ctx)
    result = asyncio.run(instance.run(task_obj))
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
