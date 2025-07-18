from supabase import Client
from app.schemas.dialogs import DialogResponse, SendMessageRequest

async def get_or_create_dialog(supabase: Client, user_id: str, article_id: int) -> DialogResponse:
    # First, try to find an existing dialog
    existing_dialog_response = supabase.table("dialogues") \
        .select("*, adapted_articles(*), messages(*)") \
        .eq("user_id", user_id) \
        .eq("adapted_article_id", article_id) \
        .single() \
        .execute()

    if existing_dialog_response.data:
        dialog_data = existing_dialog_response.data
        return DialogResponse(
            dialogId=dialog_data['id'],
            article=dialog_data['adapted_articles'],
            messages=dialog_data['messages']
        )

    # If no dialog exists, create a new one
    new_dialog_response = supabase.table("dialogues") \
        .insert({"user_id": user_id, "adapted_article_id": article_id}) \
        .execute()

    if not new_dialog_response.data:
        raise Exception("Failed to create dialog")

    new_dialog_data = new_dialog_response.data[0]

    # Fetch the newly created dialog with all related data
    created_dialog_response = supabase.table("dialogues") \
        .select("*, adapted_articles(*), messages(*)") \
        .eq("id", new_dialog_data['id']) \
        .single() \
        .execute()

    if not created_dialog_response.data:
        raise Exception("Failed to fetch created dialog")

    dialog_data = created_dialog_response.data
    return DialogResponse(
        dialogId=dialog_data['id'],
        article=dialog_data['adapted_articles'],
        messages=dialog_data['messages']
    )

async def add_message_to_dialog(supabase: Client, dialog_id: str, user_id: str, message: SendMessageRequest):
    # Save user message
    user_message_response = supabase.table("messages") \
        .insert({
            "dialogue_id": dialog_id,
            "speaker": "User",
            "content": {"text": message.message}
        }) \
        .execute()

    if not user_message_response.data:
        raise Exception("Failed to save user message")

    # TODO: Get response from AI coach

    # Save AI message
    ai_message_response = supabase.table("messages") \
        .insert({
            "dialogue_id": dialog_id,
            "speaker": "AI",
            "content": {"text": "This is a placeholder response from the AI coach."}
        }) \
        .execute()

    if not ai_message_response.data:
        raise Exception("Failed to save AI message")

    # Fetch all messages for the dialog
    messages_response = supabase.table("messages") \
        .select("*") \
        .eq("dialogue_id", dialog_id) \
        .execute()

    return messages_response.data