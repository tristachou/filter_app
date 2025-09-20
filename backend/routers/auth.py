from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict

from utils.cognito_auth import cognito_authenticator

# --- Router --- #
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# Define the security scheme (Bearer Token)
oauth2_scheme = HTTPBearer()

# --- Dependency for Getting Current User Claims from Cognito Token --- #
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Dependency that verifies the Cognito JWT and returns the user claims.
    The `token` object is an instance of `HTTPAuthorizationCredentials`.
    """
    try:
        # The actual token string is in `token.credentials`
        payload = cognito_authenticator.verify_token(token.credentials)
        return payload
    except HTTPException as e:
        # Re-raise the exception from the authenticator
        raise e
    except Exception:
        # Catch any other unexpected errors during token verification
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Endpoints --- #
@router.get("/users/me", response_model=Dict)
async def read_users_me(user_claims: Dict = Depends(get_current_user)):
    """
    Returns the claims of the currently authenticated user from their Cognito token.
    """
    return user_claims