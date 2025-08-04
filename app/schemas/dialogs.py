from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.schemas.articles import AdaptedArticleData

class Message(BaseModel):
    messageId: str
    sender: str
    text: str
    metadata: Optional[Dict[str, Any]]
    timestamp: str

class DialogResponse(BaseModel):
    dialogId: str
    article: AdaptedArticleData
    messages: List[Message]

class SendMessageRequest(BaseModel):
    message: str

class SimpleMessage(BaseModel):
    sender: str
    text: str

class DialogFollowUPRequestLLMSchema(BaseModel):
    article: str
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
    errorReview: Optional[str]
    correctedResponse: str
    grammarExplanation: Optional[str]
    followUpQuestion: str
    followUpTranslation: str
    followUpGrammarTopic: Optional[str] = None
    usedVocabulary: Dict[str, str]
