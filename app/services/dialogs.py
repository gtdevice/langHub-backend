from typing import List

from supabase import Client
from app.schemas.dialogs import DialogResponse, SendMessageRequest
from app.services.articles import get_article_by_id
from app.services.prompt_service import PromptService
from app.services.user_settings import get_user_settings

async def get_or_create_dialog(supabase: Client, user_id: str, adapted_article_id: int) -> DialogResponse:
    # First, try to find an existing dialognew_dialog_response
    existing_dialog_response = supabase.table("dialogues") \
        .select("*, adapted_articles(*), messages(*)") \
        .eq("user_id", user_id) \
        .eq("adapted_article_id", adapted_article_id).maybe_single().execute() \

    if existing_dialog_response and existing_dialog_response.data:
        dialog_data = existing_dialog_response.data
        return DialogResponse(
            dialogId=dialog_data['id'],
            article=dialog_data['adapted_articles'],
            messages=dialog_data['messages']
        )

    # If no dialog exists, create a new one
    new_dialog_response = supabase.table("dialogues") \
        .insert({"user_id": user_id, "adapted_article_id": adapted_article_id}) \
        .execute()

    if not new_dialog_response.data:
        raise Exception("Failed to create dialog")

    dialog_data = new_dialog_response.data[0]
    # get adapted article details
    articleData = get_article_by_id(supabase, adapted_article_id)
    if not articleData:
        raise Exception("Adapted article not found")
    # mapper from ArticleListItem to article schema

    return DialogResponse(
        dialogId=dialog_data['id'],
        article=await articleData,
        #empty list for messages, they will be added later
        messages= []
    )

async def get_all_dialogs(supabase: Client, user_id: str) -> List[DialogResponse]:
    # Fetch all dialogs for the user
    dialogs_response = supabase.table("dialogues") \
        .select("*, adapted_articles(*)") \
        .eq("user_id", user_id) \
        .execute()

    if not dialogs_response.data:
        return []

    dialogs = []
    for dialog_data in dialogs_response.data:
        dialogs.append(DialogResponse(
            dialogId=dialog_data['id'],
            article=dialog_data['adapted_articles'],
            messages=[]  # No need to fetch messages here, they can be fetched later
        ))

    return dialogs

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

    # Fetch dialog context (adapted_article_text and messages from whole dialog)
    dialogs_data = supabase.table("dialogues").select("id, adapted_article_id").eq("id", dialog_id).single().execute()
    if not dialogs_data.data:
        raise Exception("Dialog not found")
    
    adapted_article_id = dialogs_data.data["adapted_article_id"]
    
    # Get adapted article text and metadata
    adapted_article = supabase.table("adapted_articles").select("id, adapted_text").eq("id", adapted_article_id).single().execute()
    if not adapted_article.data:
        raise Exception("Adapted article not found")
    
    adapted_article_data = adapted_article.data
    adapted_text = adapted_article_data["adapted_text"]

    # Extract vocabulary and grammar from article metadata
    vocabulary = []
    grammar_topics = []
    
    # Get all messages in the dialog
    messages_response = supabase.table("messages").select("*").eq("dialogue_id", dialog_id).execute()
    messages = messages_response.data
    messages_sorted = sorted(messages, key=lambda x: x['created_at'])

    # Build conversation history for LLM
    from app.schemas.dialogs import SimpleMessage
    history = []
    for msg in messages_sorted:
        history.append(SimpleMessage(
            sender=msg['speaker'],
            text=msg['content']['text']
        ))


    # Get prompt template

    prompt_template = PromptService.get_dialog_follow_up_prompt()

    # Prepare LLM request using schema
    from app.schemas.dialogs import DialogFollowUPRequestLLMSchema
    llm_request = DialogFollowUPRequestLLMSchema(
        article=adapted_text,
        dialogHistory=history,
        lastUserMessage=message.message,
        vocabulary=vocabulary,
        grammarTopics=grammar_topics
    )

    #get user settings
    settings = get_user_settings(supabase, user_id)
    additional_args = {
        "lang_level": settings.language_level,
        "main_language": settings.main_language,
        "learning_language": settings.learning_language,
    }

    # Call LLM
    from app.services.llmclient import callLLM
    from app.schemas.dialogs import DialogFollowUpResponseLLMSchema
    try:
        llm_response = await callLLM(
            prompt_template_str=prompt_template,
            prompt_args=llm_request.dict() | additional_args,
            output_schema=DialogFollowUpResponseLLMSchema
        )
        ai_text = llm_response.coachResponse.text
    except Exception as e:
        # Fallback to placeholder on error
        ai_text = "I encountered an error. Please try again."

    # Save actual AI response with metadata
    ai_message_response = supabase.table("messages") \
        .insert({
            "dialogue_id": dialog_id,
            "speaker": "AI",
            "content": {
                "text": ai_text,
                "metadata": llm_response.dict()
            }
        }) \
        .execute()

    if not ai_message_response.data:
        raise Exception("Failed to save AI message")

    # Fetch all messages for the dialog including the new AI response
    messages_response = supabase.table("messages") \
        .select("*") \
        .eq("dialogue_id", dialog_id) \
        .execute()

    return messages_response.data