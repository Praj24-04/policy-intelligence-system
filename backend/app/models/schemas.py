from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# ── Auth Schemas ────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

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