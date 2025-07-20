from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.api.deps import get_supabase_client, get_current_user, get_current_user_supabase_client
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
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_current_user_supabase_client)
):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return await get_or_create_dialog_service(supabase, user_id, adapted_article_id)

@router.post("/{dialog_id}/messages", response_model=List[Message])
async def send_message_to_dialog(
    dialog_id: str,
    request: SendMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_current_user_supabase_client)
):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return await add_message_to_dialog_service(supabase, dialog_id, user_id, request)
