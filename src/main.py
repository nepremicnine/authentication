from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from src.models import (
    SignupRequest, LoginRequest, UpdatePasswordRequest,
    DeleteUserRequest, RefreshTokenRequest
)
import os
from dotenv import load_dotenv  # Import dotenv
from src.auth_handler import verify_jwt_token
import httpx
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Environment variable configurations
AUTHENTICATION_SERVER_MODE = os.getenv("AUTHENTICATION_SERVER_MODE", "debug")
AUTHENTICATION_HTTP_SERVER_PORT = int(
    os.getenv("AUTHENTICATION_HTTP_SERVER_PORT", 8080))
AUTHENTICATION_PREFIX = f"/authentication" if AUTHENTICATION_SERVER_MODE == "release" else ""
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_MANAGING_API_URL = os.getenv("USER_MANAGING_API_URL")

# FastAPI app
app = FastAPI(
    title="Authentication API",
    description="API for managing user authentication.",
    version="1.0.0",
    openapi_url=f"{AUTHENTICATION_PREFIX}/openapi.json",
    docs_url=f"{AUTHENTICATION_PREFIX}/docs",
    redoc_url=f"{AUTHENTICATION_PREFIX}/redoc",
)

origins = [
    FRONTEND_URL,
    BACKEND_URL,
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security and Supabase configurations
security = HTTPBearer()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "Missing SUPABASE_URL, SUPABASE_KEY, or SUPABASE_SERVICE_ROLE_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Endpoints


@app.get(f"{AUTHENTICATION_PREFIX}/")
async def root():
    return {"message": "Hello World"}


@app.post(f"{AUTHENTICATION_PREFIX}/signup")
async def signup(request: SignupRequest):
    try:
        user = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })

        if user:
            # Call an API for user management here
            user_data = {
                "id": user.user.id,
                "email": request.email,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "location": request.location_name,
                "latitude": request.lat,
                "longitude": request.long,
            }

            headers = {
                "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{USER_MANAGING_API_URL}/users",
                    json=user_data,
                    headers=headers,
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("message", "Error creating user in user management API"),
                )

            return user

        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(f"{AUTHENTICATION_PREFIX}/login")
async def login(request: LoginRequest):
    try:
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(f"{AUTHENTICATION_PREFIX}/update_password")
async def update_password(request: UpdatePasswordRequest):
    try:
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.old_password
        })
        updated_user = supabase.auth.update_user({
            "password": request.new_password
        })
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(f"{AUTHENTICATION_PREFIX}/delete_user")
async def delete_user(request: DeleteUserRequest):
    try:
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        deleted_user = supabase.auth.admin.delete_user(user.user.id)
        return deleted_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(f"{AUTHENTICATION_PREFIX}/auth/me", dependencies=[Depends(verify_jwt_token)])
async def get_user_details():
    try:
        response = supabase.auth.get_user()
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(f"{AUTHENTICATION_PREFIX}/refresh_token", dependencies=[Depends(verify_jwt_token)])
async def refresh_token(request: RefreshTokenRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
        headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
        payload = {"refresh_token": request.refresh_token}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
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
        raise HTTPException(status_code=500, detail=str(
            e) or "Unexpected error refreshing access token.")


@app.get(f"{AUTHENTICATION_PREFIX}/health")
async def health():
    return {"status": "ok"}
