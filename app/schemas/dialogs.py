from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Article(BaseModel):
    articleId: str
    title: str
    adaptedText: str
    category: str
    language: str
    level: str
    metadata: Dict[str, Any]

class Message(BaseModel):
    messageId: str
    sender: str
    text: str
    metadata: Dict[str, Any]
    timestamp: str

class DialogResponse(BaseModel):
    dialogId: str
    article: Article
    messages: List[Message]

class SendMessageRequest(BaseModel):
    message: str
