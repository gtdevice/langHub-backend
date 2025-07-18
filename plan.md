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

## DB Schema

```sql
-- =================================================================
-- Articles Tables
-- =================================================================

-- Create the 'articles' table to store the original, source content.
CREATE TABLE public.articles (
  id BIGSERIAL PRIMARY KEY,
  original_text TEXT NOT NULL,
  category TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.articles IS 'Stores original, unadapted article content.';

-- Create the 'adapted_articles' table for different versions of an article.
-- Each row is a specific adaptation for a language and level.
CREATE TABLE public.adapted_articles (
  id BIGSERIAL PRIMARY KEY,
  original_article_id BIGINT NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
  language TEXT NOT NULL,
  level TEXT NOT NULL,
  title TEXT NOT NULL,
  thumbnail_url TEXT,
  intro TEXT,
  adapted_text TEXT NOT NULL,
  metadata JSONB NOT NULL,
  dialogue_starter_question TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.adapted_articles IS 'Stores versions of articles adapted for specific languages and levels.';
COMMENT ON COLUMN public.adapted_articles.dialogue_starter_question IS 'The initial question to start a conversation with the user.';
COMMENT ON COLUMN public.adapted_articles.metadata IS 'Stores translation of the article and its words.';

-- =================================================================
-- Dialogue Tables
-- =================================================================

-- Create the 'dialogues' table to store conversation threads.
-- This table now links to a specific adapted article.
CREATE TABLE public.dialogues (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  adapted_article_id BIGINT NOT NULL REFERENCES public.adapted_articles(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.dialogues IS 'Stores individual dialogue sessions/threads.';
COMMENT ON COLUMN public.dialogues.adapted_article_id IS 'Links the dialogue to a specific version of an article.';

-- Create the 'messages' table to store each message within a dialogue.
CREATE TABLE public.messages (
  id BIGSERIAL PRIMARY KEY,
  dialogue_id uuid NOT NULL REFERENCES public.dialogues(id) ON DELETE CASCADE,
  speaker TEXT NOT NULL CHECK (speaker IN ('User', 'AI')),
  content JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.messages IS 'Stores each message within a dialogue.';
COMMENT ON COLUMN public.messages.content IS 'The actual message content, stored as a flexible JSONB object.';


-- =================================================================
-- Row Level Security (RLS) Policies
-- =================================================================

-- Enable RLS for all tables.
ALTER TABLE public.articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.adapted_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dialogues ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Policies for Articles: Allow any authenticated user to read articles.
CREATE POLICY "Authenticated users can read articles"
ON public.articles FOR SELECT
USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can read adapted articles"
ON public.adapted_articles FOR SELECT
USING (auth.role() = 'authenticated');

-- Policies for Dialogues: Users can only manage their own data.
CREATE POLICY "Users can manage their own dialogues"
ON public.dialogues FOR ALL
USING (auth.uid() = user_id);

CREATE POLICY "Users can manage messages in their own dialogues"
ON public.messages FOR ALL
USING (
  EXISTS (
    SELECT 1
    FROM public.dialogues d
    WHERE d.id = messages.dialogue_id AND d.user_id = auth.uid()
  )
);
```