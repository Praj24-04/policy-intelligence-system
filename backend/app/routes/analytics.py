from fastapi import APIRouter
from app.services.aggregator import (
    get_overview, get_country_distribution,
    get_sector_distribution, get_region_distribution,
    get_year_trend, get_status_distribution
)

router = APIRouter()

@router.get("/overview")   
def overview():    return get_overview()

@router.get("/countries")  
def countries():   return get_country_distribution()

@router.get("/sectors")    
def sectors():     return get_sector_distribution()

@router.get("/regions")    
def regions():     return get_region_distribution()

@router.get("/trends")     
def trends():      return get_year_trend()

@router.get("/status")     
def status():      return get_status_distribution()