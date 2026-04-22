from pydantic import BaseModel
from typing import List, Optional

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