from __future__ import annotations

import asyncio
import json
from typing import Any

from agents.shared.contracts import MCPCommand, MCPResponse

UNREAL_MCP_HOST = "localhost"
UNREAL_MCP_PORT = 55557


class MCPClient:
    """Async TCP client for the chongdashu/unreal-mcp server (port 55557).

    Usage::

        async with MCPClient() as client:
            response = await client.send_command(
                MCPCommand(type="get_scene_info")
            )
    """

    def __init__(self, host: str = UNREAL_MCP_HOST, port: int = UNREAL_MCP_PORT) -> None:
        self.host = host
        self.port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def connect(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)

    async def disconnect(self) -> None:
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def __aenter__(self) -> MCPClient:
        await self.connect()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.disconnect()

    async def send_command(self, command: MCPCommand) -> MCPResponse:
        if self._writer is None or self._reader is None:
            raise RuntimeError(
                "Not connected. Use 'async with MCPClient() as client:' or call connect() first."
            )

        payload = json.dumps(command.model_dump()).encode() + b"\n"
        self._writer.write(payload)
        await self._writer.drain()

        raw = await self._reader.readline()
        data = json.loads(raw.decode())
        return MCPResponse(**data)

    async def get_scene_info(self) -> MCPResponse:
        return await self.send_command(MCPCommand(type="get_scene_info"))

    async def create_object(
        self,
        class_name: str,
        asset_path: str,
        location: tuple[float, float, float] = (0.0, 0.0, 0.0),
        rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
        scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
        name: str = "",
    ) -> MCPResponse:
        return await self.send_command(
            MCPCommand(
                type="create_object",
                params={
                    "class_name": class_name,
                    "asset_path": asset_path,
                    "location": list(location),
                    "rotation": list(rotation),
                    "scale": list(scale),
                    "name": name,
                },
            )
        )

    async def execute_python(self, script: str) -> MCPResponse:
        return await self.send_command(
            MCPCommand(type="execute_python", params={"script": script})
        )
