from fastapi import APIRouter
from app.api.v1.articles import router as articles_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()


# Include articles routes
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])

# Include admin routes
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
