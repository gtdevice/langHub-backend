User flow:
go to the dashboard: get data directly from the supabase (user, language, level, last login, vocabularies, etc.) - no need in the API endpoint
go to the articles: GET /articles(language, level, category) - output: {articleId, title, introText, thumbnail, category, language, level}
choose an article to work with: chatForArticle(articleId) - output: {id, title, adaptedText, thumbnail, category, language, level, metadata:{dictionary, Grammar}, Dialog[dialog messages]}
send a message to the article: sendAMessageToArticle(articleId, dialogId, message) - output (answer from the llm): {id, dialogId, sampleCorrection, followupQuestion, metadata:{dictionary, Grammar}}

### 1. Get Article List
This endpoint remains the same. It's just for Browse potential articles.

Endpoint: GET /articles
Query Parameters:
* category (optional, string): e.g., "tech", "travel"
* language (optional, string): e.g., "en", "de"
* level (optional, string): e.g., "A1", "B2"

Description: Retrieves a list(3) of articles for the user to choose from.

Response:

```json
[
  { "articleId": "art_123", "title": "Die Zukunft...", "introText": "...", "thumbnail": "...", "category": "Technology", "language": "German", "level": "B1" },
] 
```

### 2. Get or Create a Dialog for an Article
This is the new, key endpoint. When a user clicks an article, they are fetching their personal dialog for it. If it doesn't exist, the backend creates it. On the backend we add userID from auth context

Endpoint: GET /dialogs/{articleId}

Description: Retrieves the user's specific dialog for a given articleId. The backend uses the authenticated user's ID and the articleId to find or create the dialog. This ensures every user gets their own private chat session with the article.

Example Response (200 OK):

```JSON

{
  "dialogId": "dlg_abc_789",
  "article": {
    "articleId": "art_123",
    "title": "Die Zukunft der deutschen Industrie",
    "adaptedText": "Die Zukunft der deutschen Industrie wird vom Klimawandel geprägt...",
    "category": "Technology",
    "language": "German",
    "level": "B1",
    "metadata": {
      "dictionary": { "Zukunft": "future", "Industrie": "industry", "...": "..." },
        "grammar": { "future_tense": "used to describe actions that will happen in the future", "passive_voice": "used to emphasize the action rather than the subject" }
    }
  },
  "messages": [
    {
      "messageId": "msg_001",
      "sender": "coach",
      "text": "Was denken Sie über dieses Thema?",
      "metadata": {
        "dictionary": { "denken": "to think", "Thema": "topic" },
        "grammar": { "modal_verbs": "used to express ability, possibility, permission, or obligation" }
      },
      "timestamp": "2025-07-16T10:30:00Z"
    }
  ]
}
```

### 3. Send a Message to a Dialog
Messages are now sent to a specific dialogId, not just a generic endpoint. This makes the action unambiguous.

Endpoint: POST /dialogs/{dialogId}/messages

Description: Sends a user's message to their specific conversation (dialogId).

Request Body:

```JSON
{
  "message": "Ich denke dass es ist ein großes Problem."
}
```
Example Response (200 OK): (Response structure is the same, but the context is now a specific dialog)

```JSON
{
  "userMessage": {
      "messageId": "msg_002",
      "sender": "user",
      "text": "Ich denke dass es ist ein großes Problem.",
      "metadata": {
      },
      "timestamp": "2025-07-16T10:30:00Z"
    },
  "corrections": {
      "sampleCorrection": "need to clarify it"
    },
  "coachResponse": {
      "messageId": "msg_003",
      "sender": "coach",
      "text": "Welche Lösungen könnten Unternehmen finden?",
      "metadata": {
        "dictionary": { "denken": "to think", "Thema": "topic" },
        "grammar": { "modal_verbs": "used to express ability, possibility, permission, or obligation" }
      },
      "timestamp": "2025-07-16T10:30:00Z"
    }
}
```
