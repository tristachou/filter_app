
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from routers import auth, media, filters, process
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

# --- Startup Event --- #
@app.on_event("startup")
def on_startup():
    """
    This function runs when the application starts.
    It ensures that the necessary storage directories exist.
    """
    print("Application starting up...")
    Path("storage/media_uploads").mkdir(parents=True, exist_ok=True)
    Path("storage/filter_uploads").mkdir(parents=True, exist_ok=True)
    Path("storage/processed_output").mkdir(parents=True, exist_ok=True)
    print("Storage directories verified.")

# --- API Routers --- #
# Note: The order of routing is important. API routers should come before the static files mount.
app.include_router(auth.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(filters.router, prefix="/api")

# Manually add the process route to bypass the router object
app.add_api_route(
    "/api/process", 
    apply_filter_to_media, 
    methods=["POST"], 
    tags=["Processing"]
)



# --- Mount Static Files (Frontend) --- #
# This must be placed AFTER the API routes
app.mount("/", StaticFiles(directory="public", html=True), name="static")


# --- Main Entry Point for Development --- #
if __name__ == "__main__":
    # This allows running the app directly with `python main.py`
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
