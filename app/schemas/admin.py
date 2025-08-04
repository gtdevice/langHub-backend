from pydantic import BaseModel, Json
from typing import Dict, Any, List
from uuid import UUID

class ProcessArticleRequest(BaseModel):
    initial_lang: str
    target_lang: str
    langLevel: str

class ProcessedArticleResponse(BaseModel):
    title: str
    adapted_text: str
    intro: str
    dialogue_starter_question: str
    dialogue_starter_question_translation: str
    metadata: Dict[str, Any]

class SimpleArticleGenerationRequest(BaseModel):
    categories: List[str]

class SimpleArticleGenerationResponse(BaseModel):
    request_id: UUID
    message: str
    estimated_articles: int
