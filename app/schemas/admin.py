from pydantic import BaseModel, Json
from typing import Dict, Any

class ProcessArticleRequest(BaseModel):
    initial_lang: str
    target_lang: str
    langLevel: str

class ProcessedArticleResponse(BaseModel):
    title: str
    adapted_text: str
    intro: str
    dialogue_starter_question: str
    metadata: Dict[str, Any]
