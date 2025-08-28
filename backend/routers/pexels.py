
import os
import httpx
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_API_URL = "https://api.pexels.com/v1/search"

@router.get("/search")
async def search_pexels(query: str = Query(..., min_length=1)):
    """
    Searches for photos on Pexels based on a query.
    """
    if not PEXELS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Pexels API key is not configured on the server.",
        )

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 15}  # Request 15 images per page

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(PEXELS_API_URL, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
            
            data = response.json()
            return {"photos": data.get("photos", [])}

        except httpx.HTTPStatusError as e:
            # Forward the error from Pexels API
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error from Pexels API: {e.response.text}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An internal server error occurred: {str(e)}",
            )
