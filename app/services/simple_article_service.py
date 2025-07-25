from typing import List
import asyncio
from uuid import UUID
from app.services.llmclient import callLLM
from pydantic import BaseModel

class ArticleResponse(BaseModel):
    title: str
    content: str
    category: str

class SimpleArticleService:
    async def generate_articles_for_categories(
        self, 
        categories: List[str], 
        user_id: str,
        supabase_client
    ) -> List[int]:
        """Generate 3 articles per category using existing LLM setup."""
        article_ids = []
        
        for category in categories:
            # Generate 3 articles per category
            for i in range(3):
                article = await self.generate_single_article(category, i+1)
                article_id = await self.store_article(article, user_id, supabase_client)
                article_ids.append(article_id)
                
                # Adapt each article using existing service
                await self.adapt_article(article_id, supabase_client)
        
        return article_ids
    
    async def generate_single_article(self, category: str, sequence: int) -> dict:
        """Generate one article using existing LLM client."""
        prompt = f"""
        Generate a simple {category} article for language learners.
        Keep it short (100-150 words) and educational.
        Return JSON: {{"title": "...", "content": "...", "category": "{category}"}}
        """
        
        response = await callLLM(
            prompt_template_str=prompt,
            prompt_args={},
            output_schema=ArticleResponse
        )
        
        return response.dict()
    
    async def store_article(self, article: dict, user_id: str, supabase_client) -> int:
        """Store article in database."""
        result = supabase_client.table("articles").insert({
            "title": article["title"],
            "content": article["content"],
            "category": article["category"],
            "user_id": user_id,
            "status": "generated"
        }).execute()
        
        return result.data[0]["id"]
    
    async def adapt_article(self, article_id: int, supabase_client):
        """Adapt article using existing service."""
        from app.services.articles import adapt_article
        
        # Get the article
        article = supabase_client.table("articles").select("*").eq("id", article_id).single().execute()
        
        # Adapt it (this will create adapted versions)
        await adapt_article(article_id, supabase_client)
    
    async def process_request_async(
        self, 
        request_id: UUID, 
        categories: List[str], 
        user_id: str, 
        supabase_client
    ):
        """Process request in background using asyncio."""
        try:
            await self.generate_articles_for_categories(categories, user_id, supabase_client)
            
            # Mark as completed
            supabase_client.table("article_generation_requests").update({
                "status": "completed",
                "completed_at": "now()"
            }).eq("id", request_id).execute()
            
        except Exception as e:
            # Simple error handling
            supabase_client.table("article_generation_requests").update({
                "status": "failed"
            }).eq("id", request_id).execute()