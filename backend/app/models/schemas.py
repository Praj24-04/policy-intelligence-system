from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ── Auth Schemas ────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., max_length=150)
    full_name: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=150)
    password: str = Field(..., max_length=100)

class GoogleLoginRequest(BaseModel):
    credential: str = Field(..., max_length=2000)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., max_length=150)

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., max_length=1000)
    new_password: str = Field(..., max_length=100)

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ── Policy Schemas ──────────────────────────────────────────────────────────
class PolicyOut(BaseModel):
    id: str
    title: str
    sector: str
    region: str
    country: str
    content: str
    tags: List[str]
    status: str
    year: Optional[int]
    version: Optional[str]
    source_url: Optional[str]
    extracted_countries: Optional[List[str]] = []

class OverviewOut(BaseModel):
    total_policies: int
    total_countries: int
    total_sectors: int
    total_regions: int

class CompareOut(BaseModel):
    policy_1: dict
    policy_2: dict
    same_sector: bool
    shared_tags: List[str]
    insights: List[str]