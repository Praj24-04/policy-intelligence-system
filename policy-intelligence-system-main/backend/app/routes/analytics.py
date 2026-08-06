from fastapi import APIRouter
from app.services.aggregator import (
    get_overview, get_country_distribution,
    get_sector_distribution, get_region_distribution,
    get_year_trend, get_status_distribution
)
from app.services.cache_service import backend_cache

router = APIRouter()

@router.get("/overview")   
def overview():
    cache_key = "analytics:overview"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached
    res = get_overview()
    backend_cache.set(cache_key, res)
    return res

@router.get("/countries")  
def countries():
    cache_key = "analytics:countries"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached
    res = get_country_distribution()
    backend_cache.set(cache_key, res)
    return res

@router.get("/sectors")    
def sectors():
    cache_key = "analytics:sectors"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached
    res = get_sector_distribution()
    backend_cache.set(cache_key, res)
    return res

@router.get("/regions")    
def regions():
    cache_key = "analytics:regions"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached
    res = get_region_distribution()
    backend_cache.set(cache_key, res)
    return res

@router.get("/trends")     
def trends():
    cache_key = "analytics:trends"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached
    res = get_year_trend()
    backend_cache.set(cache_key, res)
    return res

@router.get("/status")     
def status():
    cache_key = "analytics:status"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached
    res = get_status_distribution()
    backend_cache.set(cache_key, res)
    return res