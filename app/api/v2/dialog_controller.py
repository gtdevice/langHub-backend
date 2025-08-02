from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_authenticated_user
from app.schemas.dialogs import DialogResponse, SendMessageRequest, DialogFollowUpResponseLLMSchema
from app.services.dialogs import (
    get_or_create_dialog as get_or_create_dialog_service,
    add_message_to_dialog as add_message_to_dialog_service
)
from typing import Dict, Any, List
from app.schemas.dialogs import Message

router = APIRouter()

@router.get("/{adapted_article_id}", response_model=DialogResponse)
async def get_or_create_dialog(
    adapted_article_id: int,
    auth_user = Depends(get_authenticated_user)
):
    """Get or create a dialog for the authenticated user and article."""
    return await get_or_create_dialog_service(auth_user.client, auth_user.user_id, adapted_article_id)

@router.post("/{dialog_id}/messages", response_model=List[Message])
async def send_message_to_dialog(
    dialog_id: str,
    request: SendMessageRequest,
    auth_user = Depends(get_authenticated_user)
):
    """Send a message to an existing dialog."""
    return await add_message_to_dialog_service(auth_user.client, dialog_id, auth_user.user_id, request)