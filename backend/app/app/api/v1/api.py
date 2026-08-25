from fastapi import APIRouter
from app.modules.auth.login_endpoint import router as login_router
from app.modules.roles.role_endpoint import router as role_router
from app.modules.users.user_endpoint import router as user_router
from app.modules.tenders.tender_endpoint import router as tender_router

api_router = APIRouter()


@api_router.get("/", tags=["healthcheck"])
async def root():
    return {"message": "Tender Tracking Microservice API is running", "status": "ok"}


api_router.include_router(login_router, prefix="/login", tags=["login"])
api_router.include_router(role_router, prefix="/role", tags=["role"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(tender_router, prefix="/tender", tags=["tender"])
