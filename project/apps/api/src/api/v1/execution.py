from __future__ import annotations

from fastapi import APIRouter

from src.core.config import settings
from src.sandbox.interfaces import ExecutionRequest as SandboxExecutionRequest
from src.sandbox.providers import MockSandbox, PistonSandbox
from src.schemas.execution import ExecutionRequest, ExecutionResponse

router = APIRouter()


async def get_sandbox():
    if settings.PISTON_BASE_URL:
        return PistonSandbox(settings.PISTON_BASE_URL)
    return MockSandbox()


@router.post("/run", response_model=ExecutionResponse)
async def execute_code(data: ExecutionRequest) -> ExecutionResponse:
    sandbox = await get_sandbox()
    request = SandboxExecutionRequest(
        code=data.code,
        language=data.language,
        timeout_ms=data.timeout_ms,
        memory_limit_mb=data.memory_limit_mb,
    )
    result = await sandbox.execute(request)
    return ExecutionResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        execution_time_ms=result.execution_time_ms,
        is_timeout=result.is_timeout,
    )
