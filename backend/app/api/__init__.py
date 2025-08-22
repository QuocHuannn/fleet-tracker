# API Routes Package
# Tổ chức tất cả API endpoints

from fastapi import APIRouter

# TODO: Import all route modules
# from .auth import router as auth_router
# from .vehicles import router as vehicles_router
# from .locations import router as locations_router  
# from .alerts import router as alerts_router
# from .geofences import router as geofences_router

# Main API router
router = APIRouter()

# TODO: Include all routers
# router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# router.include_router(vehicles_router, prefix="/vehicles", tags=["Vehicles"])
# router.include_router(locations_router, prefix="/locations", tags=["Locations"])
# router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"]) 
# router.include_router(geofences_router, prefix="/geofences", tags=["Geofences"])

@router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Fleet Tracker API v1",
        "documentation": "/docs"
    }
