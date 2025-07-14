from fastapi import FastAPI
from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_str)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}