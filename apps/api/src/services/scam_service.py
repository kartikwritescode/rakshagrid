# apps/api/src/services/scam_service.py
"""
Service layer for scam call interception and real-time streaming analysis.

Implements true Server-Sent Events (SSE) generator.
Runs CPU-heavy inference on worker threads to keep event loop unblocked.
Enforces cancellation and cleanup handlers.
"""

import json
import asyncio
from typing import AsyncGenerator
from fastapi import Request
from rakshagrid.common.exceptions.base import ValidationException
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_scam.predict import (
    predict as scam_predict,
    evaluate_stream_chunk,
    stream_predict as scam_stream_predict,
)

logger = setup_logger("rakshagrid.api.scam_service")


class ScamService:
    """Encapsulates business and orchestration logic for scam text interception."""

    def analyze_text(self, transcript: str) -> dict:
        """Processes a call transcript through the multi-tier ensemble."""
        if not transcript or not transcript.strip():
            raise ValidationException("Transcript text cannot be empty.")
        return scam_predict(transcript)

    def stream_predict_batch(self, transcript_chunks: list[str]) -> list[dict]:
        """Processes incremental stream chunks synchronously (batch helper)."""
        return scam_stream_predict(transcript_chunks)

    async def generate_sse_stream(
        self,
        transcript_chunks: list[str],
        request: Request | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Progressively yields SSE events for transcript chunks.
        Event types:
          - 'event: analysis' for each incremental chunk
          - 'event: complete' with cumulative classification verdict
        Preserves cancellation cleanup and runs heavy inference in worker threads.
        """
        running_text = ""
        total_chunks = len(transcript_chunks)

        try:
            for index, chunk in enumerate(transcript_chunks):
                # Check for client cancellation
                if request is not None and await request.is_disconnected():
                    logger.info(f"SSE client disconnected at chunk {index}/{total_chunks}. Aborting stream.")
                    break

                chunk_text = chunk.strip() if chunk else ""
                running_text += (" " if running_text else "") + chunk_text

                # Offload feature extraction and scoring to worker thread
                chunk_eval = await asyncio.to_thread(evaluate_stream_chunk, running_text)

                event_data = {
                    "chunk_index": index,
                    "total_chunks": total_chunks,
                    "chunk": chunk_text,
                    "cumulative_length": len(running_text),
                    "risk_score": chunk_eval["risk_score"],
                    "risk_band": chunk_eval["risk_band"],
                    "fired_features": chunk_eval["fired_features"],
                    "fired_details": chunk_eval["fired_details"],
                }

                yield f"event: analysis\ndata: {json.dumps(event_data)}\n\n"

                # Brief async sleep to allow transport flush
                await asyncio.sleep(0.005)

            # Final complete event with full stacked ensemble verdict
            if running_text.strip():
                verdict = await asyncio.to_thread(scam_predict, running_text)
                complete_data = {
                    "status": "completed",
                    "total_chunks_processed": total_chunks,
                    "transcript": running_text,
                    "final_score": verdict["risk_score"],
                    "final_band": verdict["risk_band"],
                    "stage": verdict["stage"],
                    "fired_features": verdict.get("fired_features", []),
                    "component_scores": verdict.get("component_scores", {}),
                    "breakdown": verdict.get("breakdown", {}),
                }
            else:
                complete_data = {
                    "status": "completed",
                    "total_chunks_processed": 0,
                    "transcript": "",
                    "final_score": 0.0,
                    "final_band": "low",
                    "stage": "empty",
                    "fired_features": [],
                    "component_scores": {},
                    "breakdown": {},
                }

            yield f"event: complete\ndata: {json.dumps(complete_data)}\n\n"

        except asyncio.CancelledError:
            logger.info("SSE generator cancelled by consumer.")
            raise
        except Exception as e:
            logger.error(f"Error during SSE generation: {e}")
            err_data = {
                "error": True,
                "code": "STREAM_PROCESSING_ERROR",
                "message": "An error occurred while streaming analysis.",
            }
            yield f"event: error\ndata: {json.dumps(err_data)}\n\n"
        finally:
            logger.debug("Finished SSE stream session.")


scam_service = ScamService()
