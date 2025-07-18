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

class SimpleMessage(BaseModel):
    sender: str
    text: str

class DialogFollowUPRequestLLMSchema(BaseModel):
    dialogHistory: List[SimpleMessage]
    lastUserMessage: str
    vocabulary: List[str]
    grammarTopics: List[str]

class Correction(BaseModel):
    sampleCorrection: str

class CoachResponse(BaseModel):
    text: str
    metadata: Dict[str, Any]

class DialogFollowUpResponseLLMSchema(BaseModel):
    userMessage: str
    corrections: Correction
    coachResponse: CoachResponse
