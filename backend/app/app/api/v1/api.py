from fastapi import APIRouter
from app.api.v1.endpoints import login, role, user, tender

api_router = APIRouter()


@api_router.get("/", tags=["healthcheck"])
async def root():
    return {"message": "Tender Tracking Microservice API is running", "status": "ok"}


api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(tender.router, prefix="/tender", tags=["tender"])
