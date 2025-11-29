"""
This module defines Pydantic models used for API request and response validation.
"""

from pydantic import BaseModel


class PointUpdate(BaseModel):
    """
    Pydantic model for updating a user's points.
    """
    group_name: str  # The name of the group whose points are to be updated.
    points: int      # The number of points to add or set.

class TransferGroupOwnershipRequest(BaseModel):
    """
    Pydantic model for requesting a transfer of group ownership.
    """
    current_group_name: str # The name of the group to transfer.
    new_owner_username: str # The username of the user who will become the new owner.

class GroupSearchResult(BaseModel):
    """
    Pydantic model for a single user in the group search results.
    """
    username: str
    group_name: str

class GroupSearchResponse(BaseModel):
    """
    Pydantic model for the response of the group search endpoint.
    """
    users: list[GroupSearchResult]