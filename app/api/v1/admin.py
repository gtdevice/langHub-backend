from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from uuid import UUID
import asyncio
from app.api.deps import get_current_user_supabase_client, get_current_user
from app.schemas.admin import ProcessArticleRequest, SimpleArticleGenerationRequest, SimpleArticleGenerationResponse
from app.services.admin_article_service import adapt_article
from app.services.simple_article_service import SimpleArticleService
from supabase import Client

router = APIRouter()

@router.post("/article/process/{article_id}")
async def process_article(
    article_id: int,
    request: ProcessArticleRequest,
    supabase: Client = Depends(get_current_user_supabase_client),
) -> str:
    """
    Process an article with the given ID.
    """
    try:
        result = await adapt_article(
            article_id=article_id,
            language_level=request.langLevel,
            initial_lang=request.initial_lang,
            target_lang=request.target_lang,
            supabase=supabase,
        )
        return str(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/articles/generate-simple", response_model=SimpleArticleGenerationResponse)
async def generate_articles_simple(
    request: SimpleArticleGenerationRequest,
    supabase: Client = Depends(get_current_user_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    """Simple synchronous article generation."""
    try:
        service = SimpleArticleService()
        
        # Store request
        request_record = {
            "user_id": current_user["id"],
            "categories": request.categories,
            "status": "processing"
        }
        
        result = supabase.table("article_generation_requests").insert(request_record).execute()
        request_id = result.data[0]["id"]
        
        # Process in background (fire and forget)
        asyncio.create_task(
            service.process_request_async(request_id, request.categories, current_user["id"], supabase)
        )
        
        return SimpleArticleGenerationResponse(
            request_id=request_id,
            message="Generation started",
            estimated_articles=len(request.categories) * 3
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/generate-simple/{request_id}")
async def get_generation_status(
    request_id: UUID,
    supabase: Client = Depends(get_current_user_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    """Check generation status."""
    result = supabase.table("article_generation_requests")\
        .select("*")\
        .eq("id", str(request_id))\
        .eq("user_id", current_user["id"])\
        .single()\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return {
        "request_id": request_id,
        "status": result.data["status"],
        "categories": result.data["categories"],
        "created_at": result.data["created_at"],
        "completed_at": result.data.get("completed_at")
    }
