"""
This module defines the API endpoints for the Field Game application,
including operations for updating points, setting points, and transferring
group ownership.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from . import models
from .dependencies import get_db
from app.models import User, Role
from app import db_utils
from field_game.data import Game

router = APIRouter()
game_instance = Game()

@router.post("/update_point")
def update_point(point_update: models.PointUpdate, db: Session = Depends(get_db)):
    """
    Updates a user's points by adding to their current score.
    Requires 'group_name', 'points', and 'game_number' in the request body.
    """
    # Validation: Check if points have already been awarded for this game to this group
    if Game.has_awarded_points(point_update.group_name, point_update.game_number):
        raise HTTPException(status_code=400, detail=f"Points for Game {point_update.game_number} have already been awarded to {point_update.group_name}.")

    # Validation: Check for negative points
    if point_update.points < 0:
        raise HTTPException(status_code=400, detail="Cannot award negative points.")

    # Validation: Check if points exceed the maximum for the game
    max_points_for_game = game_instance.game_max_points.get(str(point_update.game_number))
    if max_points_for_game is not None and point_update.points > max_points_for_game:
        raise HTTPException(status_code=400, detail=f"Points awarded ({point_update.points}) exceed the maximum of {max_points_for_game} for Game {point_update.game_number}.")

    user = db.query(User).filter(User.group_name == point_update.group_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="Group not found")
    if user.point is None:
        user.point = 0
    
    user.point += point_update.points
    db.commit()
    db.refresh(user)

    # Record the point award in the static variable
    Game.add_awarded_points(point_update.group_name, point_update.game_number, point_update.points)
    
    return user

# @router.post("/set_point")
# def set_point(point_update: models.PointUpdate, db: Session = Depends(get_db)):
#     """
#     Sets a user's points to a specific score, overwriting the current value.
#     Requires 'group_name' and 'points' in the request body.
#     """
#     user = db.query(User).filter(User.group_name == point_update.group_name).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Group not found")
#     if user.point is None:
#         user.point = 0
#     user.point = point_update.points
#     db.commit()
#     db.refresh(user)
#     return user

@router.get("/")
def read_root():
    """
    Root endpoint for the API.
    Returns a welcome message.
    """
    return {"message": "Welcome to the Field Game API"}

@router.post("/transfer_group_ownership")
async def transfer_group_ownership_endpoint(
    request: models.TransferGroupOwnershipRequest,
    db: Session = Depends(get_db),
    x_user_role: str = Header(None) 
):
    """
    Transfers ownership of a game group from its current owner to a new user.
    Requires ADMIN role for authorization.

    Args:
        request: TransferGroupOwnershipRequest object containing current_group_name and new_owner_username.
        db: The SQLAlchemy database session.
        x_user_role: The role of the user making the request (from X-User-Role header).

    Raises:
        HTTPException 403: If the user role is not ADMIN.
        HTTPException 400: If the transfer operation fails.

    Returns:
        A dictionary with a success message.
    """
    if x_user_role != Role.ADMIN.name:
        raise HTTPException(status_code=403, detail="Only ADMINs can transfer group ownership.")
    
    result = await db_utils.transfer_group_ownership(
        current_group_name=request.current_group_name,
        new_owner_username=request.new_owner_username,
        db=db
    )
    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"message": result}

@router.get("/search_groups", response_model=models.GroupSearchResponse)
def search_groups(q: str, db: Session = Depends(get_db)):
    """
    Searches for groups by name.
    """
    users = db.query(User).filter(User.group_name.ilike(f"%{q}%")).all()
    print("users:", users)
    return {"users": users}