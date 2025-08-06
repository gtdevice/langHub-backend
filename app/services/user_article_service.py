"""Service for managing user article assignments using Supabase."""
from typing import List, Dict, Any
from supabase import Client

from app.services.article_generator import SimpleArticleService
from app.services.dialogs import get_all_dialogs
from app.schemas.articles import DiscoverArticleData
from app.services import get_user_settings, article_adaptor


class UserArticleService:
    """Service for handling user article generation and assignment with Supabase."""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def get_user_assigned_articles(self, user_id: str, limit: int = 5, offset: int = 0) -> List[DiscoverArticleData]:
        """Get articles assigned to a specific user."""
        
        # Query to get user's assigned articles
        response = self.supabase.table("user_x_adopted_article").select(
            "adopted_article_id, created_at"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(limit).offset(offset).execute()
        
        if not response.data:
            return []
        
        # Get the adapted articles details
        article_ids = [row["adopted_article_id"] for row in response.data]
        if not article_ids:
            return []
        
        articles_response = self.supabase.table("adapted_articles").select(
            "*"
        ).in_("id", article_ids).execute()

        # List[DialogResponse]
        all_dialogs = await get_all_dialogs(self.supabase, user_id) if user_id else []
        # Compile DiscoverArticleData from articles and dialogs

        discover_articles = []
        for article in articles_response.data or []:
            #get the article object
            article = article_adaptor.AdaptedArticleData.model_validate(article)
            # Find matching dialog for the article
            matching_dialog = next((dialog for dialog in all_dialogs if dialog.article.id == article.id), None)
            # Create DiscoverArticleData entry
            discover_article = DiscoverArticleData(
                title=article.title,
                thumbnail_url=article.thumbnail_url,
                intro=article.intro,
                adapted_article_id=article.id,
                dialogue_id=matching_dialog.dialogId if matching_dialog else None,
                created_at=None
            )
            discover_articles.append(discover_article)

        return discover_articles

    async def get_adapted_article_for_user_gt_id(self, last_id: int, count: int, language:str, level:str, categories:list[str] ) -> List[Dict[str, Any]]:

        query = self.supabase.table("adapted_articles").select("id", "original_article_id")

        # Apply filters if provided (ideally must be provided)
        if language:
            query = query.eq("language", language)
        if level:
            query = query.eq("level", level)
        if categories:
            query = query.in_("category", categories)


        adapted_response = query.gt("id", last_id).order("id", desc=False).limit(count).execute()
        if not adapted_response.data:
            return []
        return adapted_response.data

    
    async def generate_and_assign_articles(self, user_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """Generate and assign new articles to a user."""

        user_preferences = await get_user_settings(self.supabase, user_id) if user_id else None

        categories = user_preferences.preferred_categories if user_preferences else []
        language = user_preferences.learning_language if user_preferences else None
        level = user_preferences.language_level if user_preferences else None
        main_language = user_preferences.main_language if user_preferences else None
        
        # Get the last assigned article ID for this user
        last_response = self.supabase.table("user_x_adopted_article").select(
            "adopted_article_id", "original_article_id"
        ).eq("user_id", user_id).order("adopted_article_id", desc=True).limit(1).execute()
        
        last_adapted_article_id = 0
        last_original_article_id = 0
        if last_response.data:
            last_adapted_article_id = last_response.data[0]["adopted_article_id"]
            last_original_article_id = last_response.data[0]["original_article_id"]

        adapted_articles_ready_to_assign = await self.get_adapted_article_for_user_gt_id(
            last_id=last_adapted_article_id,
            count=count,
            language=language,
            level=level,
            categories=categories
        )



        #the articles to assign that are have ID greater than last_id that user have
        #articles_to_assign = adapted_response.data or []
        #here we have IDs of articles to assign as a plain list
        articles_id_pairs_to_assign = [
            {"id": article["id"], "original_article_id": article["original_article_id"]}
            for article in adapted_articles_ready_to_assign
        ]

        # If we need more articles, create new adapted articles
        if len(adapted_articles_ready_to_assign) < count:
            # we need to add at least need_count articles
            needed_count = count - len(adapted_articles_ready_to_assign)

            # get the last element from articles_to_assign list and get the original_article_id from there
            last_article_id = adapted_articles_ready_to_assign[-1]["original_article_id"] if len(adapted_articles_ready_to_assign) > 0 else last_original_article_id

            # Find new articles to adapt
            articles_to_adapt = self.supabase.table("articles").select(
                "id"
            ).gt("id", last_article_id).in_("category", categories).order("id", desc=False).limit(needed_count).execute()

            #If there are no new articles, we need to create some
            ids_to_adapt = [article["id"] for article in articles_to_adapt.data] if articles_to_adapt.data else []
            if not articles_to_adapt.data or len(articles_to_adapt.data) < needed_count:
                article_generator = SimpleArticleService()
                new_articles_ids = await article_generator.generate_articles_for_categories(
                    categories=categories,
                    user_id=user_id,
                    supabase_client=self.supabase,
                    limit=needed_count
                )
                ids_to_adapt.extend(new_articles_ids)

            
            # For each new article, create adapted version (simplified)
            for article in ids_to_adapt or []:
                adapted_article = await article_adaptor.adapt_article(
                    article_id=article,
                    language_level=level,
                    initial_lang=main_language,
                    target_lang=language,
                    supabase=self.supabase
                )
                articles_id_pairs_to_assign.append({"id": adapted_article.id, "original_article_id": adapted_article.original_article_id})
        
        # Assign articles to user
        assigned_articles = []
        for id_pair in articles_id_pairs_to_assign[:count]:

            # Assign article to user
            self.supabase.table("user_x_adopted_article").insert({
                "user_id": user_id,
                "adopted_article_id": id_pair["id"],
                "original_article_id": id_pair["original_article_id"]
            }).execute()

            assigned_articles.append({
                "id": id_pair["id"],
            })
        
        return assigned_articles

