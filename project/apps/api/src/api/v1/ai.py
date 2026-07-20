from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.ai.manager import get_ai_manager
from src.ai.protocols import Message, Role
from src.schemas.ai import (
    ChatRequest,
    ChatResponse,
    CodeReviewRequest,
    CodeReviewResponse,
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest) -> ChatResponse:
    if not data.messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    manager = get_ai_manager()
    messages = [
        Message(role=Role.USER if m.role == "user" else Role.ASSISTANT, content=m.content)
        for m in data.messages
    ]

    response = await manager.generate(messages, data.temperature, data.max_tokens)
    return ChatResponse(content=response, model="")


@router.post("/chat/stream")
async def chat_stream(data: ChatRequest):
    if not data.messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    manager = get_ai_manager()
    messages = [
        Message(role=Role.USER if m.role == "user" else Role.ASSISTANT, content=m.content)
        for m in data.messages
    ]

    async def event_generator():
        async for chunk in manager.generate_stream(messages, data.temperature, data.max_tokens):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/code-review", response_model=CodeReviewResponse)
async def code_review(data: CodeReviewRequest) -> CodeReviewResponse:
    manager = get_ai_manager()
    context = data.context or ""
    prompt = f"""Review the following {data.language} code for correctness, style, performance, and edge cases.

{context}

```{data.language}
{data.code}
```

Provide feedback, specific suggestions for improvement, and identify any issues or bugs."""

    messages = [Message(role=Role.USER, content=prompt)]
    response = await manager.generate(messages)

    return CodeReviewResponse(
        feedback=response,
        suggestions=[],
        issues=[],
    )


@router.post("/hints", response_model=ChatResponse)
async def generate_hint(concept_slug: str, problem: str) -> ChatResponse:
    manager = get_ai_manager()
    prompt = f"""You are a programming mentor. A learner is working on a problem about "{concept_slug}".

Problem: {problem}

Provide a helpful hint that guides them toward the solution without giving it away completely."""

    messages = [Message(role=Role.USER, content=prompt)]
    response = await manager.generate(messages)
    return ChatResponse(content=response, model="")
