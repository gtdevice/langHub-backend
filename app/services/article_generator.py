from typing import List

from app.services import prompt_service
from app.services.llmclient import callLLM
from pydantic import BaseModel
from app.services.prompt_service import PromptService

class ArticleResponse(BaseModel):
    title: str
    content: str
    category: str


class SimpleArticleService:
    async def generate_articles_for_categories(
            self,
            categories: List[str],
            user_id: str,
            supabase_client,
            limit: int = 3
    ) -> List[int]:
        """Generate 3 articles per category using existing LLM setup."""
        article_ids = []

        for category in categories:
            # Generate 3 articles per category
            for i in range(limit):
                article = await self.generate_single_article(category, i + 1)
                article_id = await self.store_article(article, user_id, supabase_client)
                article_ids.append(article_id)

        return article_ids

    async def generate_single_article(self, category: str, sequence: int) -> dict:
        """Generate one article using existing LLM client."""
        prompt = PromptService.get_article_creation_prompt()
        #get current date
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

        response = await callLLM(
            prompt_template_str=prompt,
            prompt_args={"category": category, "date": date },
            output_schema=ArticleResponse,
            extended_model=True
        )

        return response.dict()

    async def store_article(self, article: dict, user_id: str, supabase_client) -> int:
        """Store article in database."""
        result = supabase_client.table("articles").insert({
            "title": article["title"],
            "original_text": article["content"],
            "category": article["category"],
            "user_id": user_id
        }).execute()

        return result.data[0]["id"]