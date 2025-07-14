from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Include user routes
api_router.include_router(users_router, prefix="/users", tags=["users"])
