from typing import List, Optional
from supabase import Client
from app.schemas.articles import ArticleListItem


async def get_articles(
    supabase: Client,
    category: Optional[str] = None,
    language: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 3
) -> List[ArticleListItem]:
    """
    Fetch articles from adapted_articles table with optional filters.
    
    Args:
        supabase: Supabase client instance
        category: Optional category filter
        language: Optional language filter  
        level: Optional level filter
        limit: Maximum number of articles to return (default: 3)
    
    Returns:
        List of ArticleListItem objects
    """
    
    # Build query
    query = supabase.table("adapted_articles").select(
        "id, title, adapted_text, thumbnail_url, language, level"
    )
    
    # Apply filters if provided
    if language:
        query = query.eq("language", language)
    if level:
        query = query.eq("level", level)
    
    # Execute query with limit
    response = query.limit(limit).execute()
    
    # Transform results to ArticleListItem format
    articles = []
    for row in response.data:
        article = ArticleListItem(
            articleId=str(row["id"]),
            title=row["title"],
            introText=row["adapted_text"] or "",
            thumbnail=row["thumbnail_url"] or "",
            language=row["language"],
            level=row["level"]
        )
        articles.append(article)
    
    return articles 