# Authentication/main.py
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from src.models import SignupRequest, LoginRequest, UpdatePasswordRequest, DeleteUserRequest, RefreshTokenRequest
import os
from dotenv import load_dotenv  # Import dotenv
from src.auth_handler import verify_jwt_token
from src.create_client_jwt import create_client_jwt
import httpx


# Load environment variables from .env file
load_dotenv()

app = FastAPI()
security = HTTPBearer()


# Replace these with your actual Supabase URL and API key
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing SUPABASE_URL, SUPABASE_KEY, or SUPABASE_SERVICE_ROLE_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Test "/"
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/signup")
async def signup(request: SignupRequest):
    try:
        # Sign up user
        user = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
   
@app.post("/login")
async def login(request: LoginRequest):
    try:
        # Log in user
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/update_password")
async def update_password(request: UpdatePasswordRequest):
    try:
        # Log in user
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.old_password
        })

        # Update password
        updated_user = supabase.auth.update_user({
            "password": request.new_password
        })

        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/delete_user")
async def delete_user(request: DeleteUserRequest):
    try:
        # Log in user
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        # Delete user
        deleted_user = supabase.auth.admin.delete_user(user.user.id)

        return deleted_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/auth/me",dependencies=[Depends(verify_jwt_token)])
async def get_user_details():
    try:
        response = supabase.auth.get_user()
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/refresh_token/",dependencies=[Depends(verify_jwt_token)])
async def refresh_token(request: RefreshTokenRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:

        # Read the token from the Authorization header
        token = credentials.credentials
        print("Token:", token)

        # Prepare the refresh token request
        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
        }
        payload = {"refresh_token": request.refresh_token}

        # Make an async request to refresh the token
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            print("Data:", data)
            return {
                "accessToken": data.get("access_token"),
                "refreshToken": data.get("refresh_token"),
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("error", "Error refreshing access token"),
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e) or "Unexpected error refreshing access token.",
        )
    
@app.get("/health")
async def health():
    return {"status": "ok"}
    

        