from pydantic import BaseModel, EmailStr, validator
from typing import ClassVar
import re

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    location_name: str
    lat: float
    long: float


    # Custom password validation
    @validator("password")
    def validate_password(cls, value):
        # Define password requirements regex
        password_regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        
        # Check if password meets requirements
        if not re.match(password_regex, value):
            raise ValueError(
                "Password must be at least 8 characters long, include at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

    # Apply the same validation to new password
    @validator("new_password")
    def validate_new_password(cls, value):
        password_regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        
        if not re.match(password_regex, value):
            raise ValueError(
                "Password must be at least 8 characters long, include at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return value

class DeleteUserRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str