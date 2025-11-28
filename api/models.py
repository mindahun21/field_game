from pydantic import BaseModel


class PointUpdate(BaseModel):
    group_name: str
    points: int

class TransferGroupOwnershipRequest(BaseModel):
    current_group_name: str
    new_owner_username: str
