from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    settings = get_settings()
    return HealthOut(status="ok", service=settings.app_name, mode=settings.environment)
