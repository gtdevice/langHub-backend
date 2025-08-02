from fastapi import APIRouter
from app.api.v2.user_controller import router as user_settings_router
from app.api.v2.dialog_controller import router as dialogs_router
from app.api.v2.article_controller import router as articles_router
from app.api.v2.admin_controller import router as admin_router


api_router = APIRouter()

api_router.include_router(user_settings_router, prefix="/users", tags=["users"])
# Include dialogs routes
api_router.include_router(dialogs_router, prefix="/dialogs", tags=["dialogs"])

# Include articles routes
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])
# Include admin routes
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])