import json
from app.services.llmclient import callLLM
from app.services.prompt_service import PromptService
from supabase import Client
import httpx
from app.schemas.articles import AdaptedArticleData
from app.schemas.admin import ProcessedArticleResponse

async def _save_adapted_article(article_data: AdaptedArticleData, supabase: Client) -> None:
    """
    Saves the adapted article to the database.
    """
    # Pydantic's model_dump_json handles the serialization correctly
    response = supabase.table("adapted_articles").insert(article_data.model_dump(mode='json')).execute()
    if not response.data:
        raise httpx.HTTPStatusError("Failed to save adapted article", request=None, response=httpx.Response(500))

async def adapt_article(
    article_id: int,
    language_level: str,
    initial_lang: str,
    target_lang: str,
    supabase: Client
) -> ProcessedArticleResponse:
    """
    Adapts an article and saves it to the database.
    """
    # Fetch article from Supabase
    response = supabase.table("articles").select("original_text", "category").eq("id", article_id).single().execute()

    if not response.data:
        raise httpx.HTTPStatusError(f"Article with id {article_id} not found", request=None, response=httpx.Response(404))

    article_data = response.data
    article_text = article_data.get("original_text")

    prompt_template = PromptService.get_article_adaptation_prompt()
    prompt_args = {
        "language_level": language_level,
        "target_lang": target_lang,
        "initial_lang": initial_lang,
        "article": article_text
    }

    processed_article = await callLLM(
        prompt_template_str=prompt_template,
        prompt_args=prompt_args,
        output_schema=ProcessedArticleResponse
    )

    # The metadata from the LLM is a dict. We need to convert it to a JSON string.
    adapted_article_data = AdaptedArticleData(
        id=None,  # Let the database assign the ID
        original_article_id=article_id,
        language=target_lang,
        level=language_level,
        title=processed_article.title,
        thumbnail_url=None,
        intro=processed_article.intro,
        adapted_text=processed_article.adapted_text,
        metadata=json.dumps(processed_article.metadata),
        dialogue_starter_question=processed_article.dialogue_starter_question
    )

    await _save_adapted_article(adapted_article_data, supabase)

    return processed_article
