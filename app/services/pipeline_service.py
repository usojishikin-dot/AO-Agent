# app/services/pipeline_service.py
import asyncio

import random

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.content_version_repository import ContentVersionRepository
from app.repositories.news_repository import NewsRepository
from app.services.cloudinary_service import transform_and_upload_image
from app.services.evaluation_engine import MAX_RETRIES, evaluate_post
from app.services.generation_engine import (
    generate_all_platforms,
    refine_one_platform,
    regenerate_one_platform,
)
from app.services.prompt_processor import ProcessedContent, process_content
from app.services.task_router import MasterOutline, generate_master_outline

logger = get_logger(__name__)

PLATFORMS = ["x", "linkedin_company", "linkedin_personal", "facebook"]


async def run_pipeline(*, news_item_id: int, trace_id: str, external_id: str) -> None:
    """
    Full AI pipeline orchestrator. Runs as a background asyncio task.

    Stages:
      1. Load news item & update status → PROCESSING
      2. Prompt Processor  — clean content + inject brand context
      3. Task Router       — Gemini Flash → MasterOutline
      4. Generation Engine — Groq Llama (3 platforms, parallel)
      5. Evaluation Engine — Gemini Pro per platform (with retry)
      6. Storage           — ContentVersion rows with scores
      7. Update status     → COMPLETED / FAILED
    """
    async with AsyncSessionLocal() as session:
        news_repo = NewsRepository(session)
        cv_repo = ContentVersionRepository(session)

        try:
            # ── 1. Load & guard ──────────────────────────────────────────────
            news_item = await news_repo.get_by_id(news_item_id)
            if not news_item:
                logger.error(
                    "News item not found — pipeline aborted",
                    extra={"trace_id": trace_id, "stage": "pipeline"},
                )
                return

            await news_repo.update_status(news_item_id, "PROCESSING")
            logger.info(
                "Pipeline started",
                extra={
                    "trace_id": trace_id,
                    "stage": "pipeline",
                    "external_id": external_id,
                },
            )

            # ── 2. Prompt Processor & Media Layer ──────────────────────────
            # Resize image to social standards immediately
            if news_item.image_url:
                transformed_url = await transform_and_upload_image(news_item.image_url)
                if transformed_url and transformed_url != news_item.image_url:
                    await news_repo.update_image_url(news_item_id, transformed_url)
                    news_item.image_url = transformed_url

            processed = process_content(
                title=news_item.title,
                content=news_item.content,
                source_url=news_item.source_url,
                image_url=news_item.image_url,
            )

            # ── 3. Task Router → Master Outline ──────────────────────────────
            outline = await generate_master_outline(processed, trace_id)
            
            # Save outline to DB for the dashboard
            outline_text = f"CORE MESSAGE: {outline.core_message}\n\nKEY POINTS:\n" + "\n".join(f"- {p}" for p in outline.key_points)
            if outline.mandatory_facts:
                outline_text += f"\n\nMANDATORY FACTS: {outline.mandatory_facts}"
            outline_text += f"\n\nAUDIENCE: {outline.audience}\nTONE: {outline.tone}"
            
            await news_repo.update_master_outline(news_item_id, outline_text)

            # ── 4. Parallel Generation ───────────────────────────────────────
            generated: dict[str, str] = await generate_all_platforms(outline, trace_id)

            # We process platforms concurrently but with a semaphore to avoid 
            # overwhelming the free-tier DB/AI APIs.
            semaphore = asyncio.Semaphore(2)
            
            async def process_platform(platform: str, initial_text: str):
                async with semaphore:
                    # Initial jitter to desynchronize starts
                    await asyncio.sleep(random.uniform(0.1, 1.5))
                    
                    post_text = initial_text
                    eval_result = None

                    # Each parallel task MUST have its own DB session
                    async with AsyncSessionLocal() as session:
                        cv_repo = ContentVersionRepository(session)
                        
                        for attempt in range(1, MAX_RETRIES + 1):
                            # Slight delay if retrying to avoid spamming the API
                            if attempt > 1:
                                await asyncio.sleep(1.0)

                            eval_result = await evaluate_post(
                                platform=platform,
                                post_text=post_text,
                                brand_context=processed.brand_context,
                                trace_id=trace_id,
                            )

                            if eval_result.passed:
                                break

                            # Failed — refine if attempts remain
                            if attempt < MAX_RETRIES:
                                logger.info(
                                    "Evaluation failed — refining",
                                    extra={
                                        "trace_id": trace_id,
                                        "stage": "evaluation",
                                        "platform": platform,
                                        "attempt": attempt,
                                        "score": eval_result.overall_score,
                                        "decision": "REFINE",
                                    },
                                )
                                # Use refinement logic (Critique & Refine)
                                post_text = await refine_one_platform(
                                    platform=platform,
                                    original_text=post_text,
                                    refinement_instructions=eval_result.refinement_instructions,
                                    trace_id=trace_id,
                                )

                        final_status = "GENERATED" if eval_result.passed else "EVALUATION_FAILED"

                        latest_version = await cv_repo.get_latest_version_number(
                            news_item_id=news_item_id,
                            platform=platform,
                        )

                        await cv_repo.create_content_version_with_scores(
                            news_item_id=news_item_id,
                            platform=platform,
                            version_number=latest_version + 1,
                            content_text=post_text,
                            status=final_status,
                            evaluation_score=eval_result.overall_score,
                            brand_score=eval_result.brand_score,
                            human_likeness_score=eval_result.human_likeness_score,
                            platform_compliance_score=eval_result.platform_compliance_score,
                            evaluation_feedback=eval_result.feedback,
                        )

                        logger.info(
                            "Content version stored",
                            extra={
                                "trace_id": trace_id,
                                "stage": "storage",
                                "platform": platform,
                                "status": final_status,
                                "overall_score": eval_result.overall_score,
                            },
                        )

            # Launch all platform evaluations concurrently
            logger.info(f"Launching processing for platforms: {[p for p in PLATFORMS if p in generated]}")
            tasks = [
                process_platform(p, generated[p]) 
                for p in PLATFORMS 
                if p in generated
            ]
            await asyncio.gather(*tasks)

            # ── 7. Mark complete ─────────────────────────────────────────────
            await news_repo.update_status(news_item_id, "COMPLETED")
            logger.info(
                "Pipeline completed",
                extra={
                    "trace_id": trace_id,
                    "stage": "pipeline",
                    "decision": "COMPLETED",
                },
            )

        except Exception as exc:
            logger.error(
                "Pipeline failed",
                extra={
                    "trace_id": trace_id,
                    "stage": "pipeline",
                    "decision": "FAILED",
                    "error": str(exc),
                },
            )
            try:
                await news_repo.update_status(news_item_id, "FAILED")
            except Exception:
                pass
            raise


def start_pipeline_task(*, news_item_id: int, trace_id: str, external_id: str) -> None:
    """Fire-and-forget: launch the pipeline as a background asyncio task."""
    asyncio.create_task(
        run_pipeline(
            news_item_id=news_item_id,
            trace_id=trace_id,
            external_id=external_id,
        )
    )