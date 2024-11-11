from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv 

# Load environment variables from .env file
load_dotenv()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

security = HTTPBearer()  # Automatically expects 'Authorization: Bearer <token>'

# Dependency for verifying the JWT token
def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials  # Extract the token
    print("Token: ", token)
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
        # If decoding succeeds, return the payload (or parts of it)
        return payload
    except Exception as e:
        # Raise an HTTP 401 error if the token is invalid or expired
        raise HTTPException(status_code=401, detail="Invalid or expired token")