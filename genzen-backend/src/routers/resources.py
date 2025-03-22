from fastapi import APIRouter, Depends
from src.utils.auth_utils import get_current_user
from src.models.models import GenZenUser
router = APIRouter()

@router.get("/")
async def get_resources():
    # TODO: Implement resource retrieval logic
    return {"message": "Resources fetched successfully"}