# apps/api/src/routers/v1/scam.py
"""Router for Module 2: Scam Call Interceptor & Digital Arrest Detection."""

import asyncio
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from apps.api.src.schemas.scam_schema import TextRequest, StreamRequest, VerdictResponse
from apps.api.src.services.scam_service import scam_service

router = APIRouter(prefix="/scam", tags=["Scam Call Interceptor"])


@router.post("/analyze-text", response_model=VerdictResponse, status_code=status.HTTP_200_OK)
async def analyze_text(payload: TextRequest):
    """
    Analyzes a call or message transcript through the feature-augmented stacked ensemble pipeline.
    Runs asynchronously on worker thread without blocking the FastAPI event loop.
    """
    if not payload.transcript or not payload.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript text cannot be empty.",
        )

    result = await asyncio.to_thread(scam_service.analyze_text, payload.transcript)
    return result


@router.post("/stream", status_code=status.HTTP_200_OK)
async def analyze_stream_chunks(payload: StreamRequest, request: Request):
    """
    Progressive real-time Server-Sent Events (SSE) streaming endpoint.
    Emits 'event: analysis' for each speech segment followed by 'event: complete'.
    Media type: text/event-stream.
    """
    if not payload.transcript_chunks or not any(c and c.strip() for c in payload.transcript_chunks):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transcript_chunks must contain at least one non-empty text chunk.",
        )

    generator = scam_service.generate_sse_stream(
        payload.transcript_chunks,
        request=request,
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
