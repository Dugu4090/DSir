from __future__ import annotations

import os

import httpx

from src.sandbox.interfaces import CodeSandbox, ExecutionRequest, ExecutionResponse


class MockSandbox(CodeSandbox):
    async def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        return ExecutionResponse(
            stdout="Mock execution output",
            stderr="",
            exit_code=0,
            execution_time_ms=1,
        )


class PistonSandbox(CodeSandbox):
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("PISTON_BASE_URL", "http://localhost:2000")

    async def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        payload = {
            "language": request.language,
            "version": "*",
            "files": [{"content": request.code}],
        }
        try:
            async with httpx.AsyncClient(timeout=request.timeout_ms / 1000) as client:
                response = await client.post(f"{self.base_url}/api/v2/execute", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException:
            return ExecutionResponse(
                stdout="",
                stderr="Execution timed out",
                exit_code=1,
                execution_time_ms=request.timeout_ms,
                is_timeout=True,
            )

        run = data.get("run", {})
        return ExecutionResponse(
            stdout=run.get("stdout", ""),
            stderr=run.get("stderr", ""),
            exit_code=run.get("code", 1),
            execution_time_ms=run.get("cpuUsage", 0),
        )
