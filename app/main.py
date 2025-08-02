from fastapi import FastAPI
from app.api.v1 import api_router as api_v1
from app.api.v2 import api_router as api_v2
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)
# WARNING: This configuration is insecure and should only be used for testing.
# It allows requests from any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API router
app.include_router(api_v1, prefix=settings.api_v1_str)
app.include_router(api_v2, prefix=settings.api_v2_str)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}