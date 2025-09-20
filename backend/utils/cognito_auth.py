
import requests
import time
from jose import jwk, jwt
from jose.exceptions import JOSEError
from fastapi import HTTPException, status

# Cognito User Pool settings from user
REGION = "ap-southeast-2"
USER_POOL_ID = "ap-southeast-2_kddUAod7A"
APP_CLIENT_ID = "4h9hjhn6bfujbskpocnd9mticd"

# Construct the URL for the JSON Web Key Set (JWKS)
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

class CognitoAuthenticator:
    def __init__(self):
        self.jwks = None
        self.cache_expiry = 0

    def _fetch_jwks(self):
        """
        Fetches the JSON Web Key Set (JWKS) from the Cognito User Pool.
        Caches the keys for 1 hour to avoid excessive requests.
        """
        current_time = time.time()
        if not self.jwks or current_time >= self.cache_expiry:
            try:
                response = requests.get(JWKS_URL)
                response.raise_for_status()
                self.jwks = response.json()["keys"]
                self.cache_expiry = current_time + 3600  # Cache for 1 hour
            except requests.exceptions.RequestException as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Could not fetch JWKS from Cognito: {e}"
                )
        return self.jwks

    def verify_token(self, token: str):
        """
        Verifies a Cognito JWT.

        Args:
            token: The JWT token string.

        Returns:
            The decoded claims from the token if verification is successful.

        Raises:
            HTTPException: If the token is invalid, expired, or has a bad signature.
        """
        jwks = self._fetch_jwks()
        
        try:
            # Get the unverified header from the token
            unverified_header = jwt.get_unverified_header(token)
        except JOSEError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token header"
            )

        # Find the key in the JWKS that matches the key ID from the token header
        rsa_key = {}
        for key in jwks:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key in JWKS"
            )

        try:
            # Decode and validate the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=APP_CLIENT_ID,
                issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
            )

            # Additional check for token_use claim
            if payload.get("token_use") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is not an access token"
                )
            
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTClaimsError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token claims: {e}"
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token"
            )

# Create a single instance to be used across the application
cognito_authenticator = CognitoAuthenticator()
