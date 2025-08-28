
import os
import httpx
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_PHOTOS_URL = "https://api.pexels.com/v1/search"
PEXELS_VIDEOS_URL = "https://api.pexels.com/videos/search"

class SearchType(str, Enum):
    PHOTOS = "photos"
    VIDEOS = "videos"

@router.get("/search")
async def search_pexels(query: str = Query(..., min_length=1), search_type: SearchType = Query(SearchType.PHOTOS)):
    """
    Searches for photos or videos on Pexels based on a query and type.
    """
    if not PEXELS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Pexels API key is not configured on the server.",
        )

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 15}

    if search_type == SearchType.VIDEOS:
        url = PEXELS_VIDEOS_URL
    else:
        url = PEXELS_PHOTOS_URL

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
            
            data = response.json()

            if search_type == SearchType.VIDEOS:
                return {"media": data.get("videos", []), "type": "videos"}
            else:
                return {"media": data.get("photos", []), "type": "photos"}

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error from Pexels API: {e.response.text}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An internal server error occurred: {str(e)}",
            )
