from supabase import Client
from app.schemas.dialogs import DialogResponse, SendMessageRequest
from app.services.articles import get_article_by_id

async def get_or_create_dialog(supabase: Client, user_id: str, adapted_article_id: int) -> DialogResponse:
    # First, try to find an existing dialognew_dialog_response
    existing_dialog_response = supabase.table("dialogues") \
        .select("*, adapted_articles(*), messages(*)") \
        .eq("user_id", user_id) \
        .eq("adapted_article_id", adapted_article_id).maybe_single().execute() \
        # .maybe_single() \
        # .execute()

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

    # new_dialog_data = new_dialog_response.data[0]

    # Fetch the newly created dialog with all related data
    # created_dialog_response = supabase.table("dialogues") \
    #     .select("*, adapted_articles(*), messages(*)") \
    #     .eq("id", new_dialog_data['id']) \
    #     .single() \
    #     .execute()

    # if not created_dialog_response.data:
    #     raise Exception("Failed to fetch created dialog")

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

    # Fetch dialog context (article + messages)
    dialog_response = supabase.table("dialogues") \
        .select("*, adapted_articles(*), messages(*)") \
        .eq("id", dialog_id) \
        .single() \
        .execute()

    if not dialog_response.data:
        raise Exception("Failed to fetch dialog context")

    dialog_data = dialog_response.data
    article = dialog_data['adapted_articles']
    messages = dialog_data['messages']

    # Sort messages by created_at
    messages_sorted = sorted(messages, key=lambda x: x['created_at'])

    # Build conversation history for LLM
    from app.schemas.dialogs import SimpleMessage
    history = []
    for msg in messages_sorted:
        history.append(SimpleMessage(
            sender=msg['speaker'],
            text=msg['content']['text']
        ))

    # Get vocabulary and grammar topics from article metadata
    vocabulary = article.get('metadata', {}).get('vocabulary', [])
    grammar_topics = article.get('metadata', {}).get('grammarTopics', [])

    # Get prompt template
    from app.services.prompt_service import PromptService
    prompt_template = PromptService.get_dialog_follow_up_prompt()

    # Prepare LLM arguments
    prompt_args = {
        "dialogHistory": history,
        "lastUserMessage": message.message,
        "vocabulary": vocabulary,
        "grammarTopics": grammar_topics
    }

    # Call LLM
    from app.services.llmclient import callLLM
    from app.schemas.dialogs import DialogFollowUpResponseLLMSchema
    try:
        llm_response = await callLLM(
            prompt_template_str=prompt_template,
            prompt_args=prompt_args,
            output_schema=DialogFollowUpResponseLLMSchema
        )
        ai_text = llm_response.coachResponse.text
    except Exception as e:
        # Fallback to placeholder on error
        ai_text = "I encountered an error. Please try again."

    # Save actual AI response
    ai_message_response = supabase.table("messages") \
        .insert({
            "dialogue_id": dialog_id,
            "speaker": "AI",
            "content": {"text": ai_text}
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