from fastapi import APIRouter, Depends, HTTPException

from uuid import UUID
import asyncio
from app.api.deps import get_current_user_supabase_client, get_current_user
from app.schemas.admin import ProcessArticleRequest, SimpleArticleGenerationRequest, SimpleArticleGenerationResponse
from app.services.article_adaptor import adapt_article
from app.services.article_generator import SimpleArticleService
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