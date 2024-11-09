# Authentication/main.py
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from models import SignupRequest, LoginRequest, UpdatePasswordRequest, DeleteUserRequest
import os
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Replace these with your actual Supabase URL and API key
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

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

        print(user)

        # Delete user
        deleted_user = supabase.auth.admin.delete_user(user.user.id)

        return deleted_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
