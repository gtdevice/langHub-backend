from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.articles import router as articles_router
from app.api.v1.dialogs import router as dialogs_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Include user routes
api_router.include_router(users_router, prefix="/users", tags=["users"])

# Include articles routes
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])

# Include dialogs routes
api_router.include_router(dialogs_router, prefix="/dialogs", tags=["dialogs"])

# Include admin routes
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
