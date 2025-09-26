
from config import load_config

# Load all configuration from AWS at startup
load_config()

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from routers import filters, media, process, auth, pexels
from routers.process import apply_filter_to_media
from routers.process import apply_filter_to_media

# --- App Initialization --- #
app = FastAPI(
    title="Web Filter App",
    description="A FastAPI application to upload media and filters, and apply them.",
    version="1.0.0",
)

# --- Middleware --- #
# Configure CORS to allow frontend development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



# --- API Routers --- #
# Note: The order of routing is important. API routers should come before the static files mount.
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router)
api_v1_router.include_router(media.router)
api_v1_router.include_router(filters.router)
api_v1_router.include_router(pexels.router)


# Manually add the process route to bypass the router object
api_v1_router.add_api_route(
    "/process", 
    apply_filter_to_media, 
    methods=["POST"], 
    tags=["Processing"]
)


app.include_router(api_v1_router) 


# --- Main Entry Point for Development --- #
if __name__ == "__main__":
    # This allows running the app directly with `python main.py`
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
