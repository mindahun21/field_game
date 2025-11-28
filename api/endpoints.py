from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from . import models
from .dependencies import get_db
from app.models import User, Role # Import Role
from app import db_utils # Import db_utils

router = APIRouter()

@router.post("/update_point")
def update_point(point_update: models.PointUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.group_name == point_update.group_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="Group not found")
    user.point += point_update.points
    db.commit()
    db.refresh(user)
    return user

@router.post("/set_point")
def set_point(point_update: models.PointUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.group_name == point_update.group_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="Group not found")
    user.point = point_update.points
    db.commit()
    db.refresh(user)
    return user

@router.get("/")
def read_root():
    return {"message": "Welcome to the Field Game API"}

@router.post("/transfer_group_ownership")
async def transfer_group_ownership_endpoint(
    request: models.TransferGroupOwnershipRequest,
    db: Session = Depends(get_db),
    x_user_role: str = Header(None) # Expect user role in a header
):
    if x_user_role != Role.ADMIN.name: # Check if the role is ADMIN (case-sensitive)
        raise HTTPException(status_code=403, detail="Only ADMINs can transfer group ownership.")
    
    result = await db_utils.transfer_group_ownership(
        current_group_name=request.current_group_name,
        new_owner_username=request.new_owner_username,
        db=db
    )
    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"message": result}

