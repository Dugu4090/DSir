from __future__ import annotations

from pydantic import BaseModel


class ExecutionRequest(BaseModel):
    code: str
    language: str
    timeout_ms: int = 3000
    memory_limit_mb: int = 128


class ExecutionResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    is_timeout: bool = False
