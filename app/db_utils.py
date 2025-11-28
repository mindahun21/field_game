from typing import Tuple, TypeVar, Union, Literal,List
from sqlalchemy import select

from .models import Role,User

T = TypeVar("T")

async def add_obj(obj,db=None):
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj

async def delete_obj(obj,db=None):
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    db.delete(obj)
    db.commit()

async def delete_all_rows(model, db=None):
    if db is None:
        raise ValueError("You didn't pass a database connection to the function")

    rows = db.query(model).all()
    for row in rows:
        db.delete(row)

    db.commit()

async def set_val(obj,db=None,**kwargs):
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    for k, v in kwargs.items():
        setattr(obj,k,v)
    
    db.add(obj)
    db.commit()

async def add_entry(obj:T,db=None,**kwargs) ->T:
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    new_entery =obj(**kwargs)
    db.add(new_entery)
    db.commit()

    return new_entery

async def remove_entry(obj,db=None,**filters):
    if db is None:
        raise ValueError("you didn't pass database connection to the function")

    stmt=select(obj).filter_by(**filters)
    entry=db.scalars(stmt).first()
    db.delete(entry)
    db.commit()

async def get_entry(obj,db=None,**filters)->Union[T,Literal[False]]:
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    stmt=select(obj).filter_by(**filters)
    entry=db.scalars(stmt).first()
    if entry:
        return entry
    
    return False

async def get_entries(obj,db=None,**filters)-> Union[List[T],Literal[False]]:
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    stmt = select(obj).filter_by(**filters)
    entries=db.scalars(stmt).all()
    if entries:
        return entries
    
    return False

async def is_group_name_taken(group_name: str, db=None) -> bool:
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    user = await get_entry(User, db=db, group_name=group_name)
    return user is not False

async def get_role(user_id:int,db=None) -> Tuple[Role,Union[User, None]]:
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    user = await get_entry(User,db=db,user_id=user_id)

    if user and user.role == Role.USER:
        return (Role.USER,user)
    elif user and user.role == Role.ADMIN:
        return (Role.ADMIN,user)
    elif user and user.role == Role.GAME_ADMIN:
        return (Role.GAME_ADMIN,user)
    
    return (Role.NONE,None)

async def transfer_group_ownership(current_group_name: str, new_owner_username: str, db=None) -> str:
    if db is None:
        return "Error: Database connection not provided."

    # 1. Find the old owner by current_group_name
    old_owner = await get_entry(User, db=db, group_name=current_group_name)
    if not old_owner:
        return f"Error: No group found with name '{current_group_name}'."
    
    # 2. Find the new owner by new_owner_username
    new_owner = await get_entry(User, db=db, username=new_owner_username)
    if not new_owner:
        return f"Error: New owner user @{new_owner_username} not found."
    
    # 3. Check if new_owner already has a group
    if new_owner.group_name:
        return f"Error: New owner @{new_owner_username} already owns group '{new_owner.group_name}'. Cannot transfer."
    
    # 4. Prevent transferring to self (if it makes sense)
    if old_owner.user_id == new_owner.user_id:
        return f"Error: User @{new_owner_username} is already the owner of group '{current_group_name}'."

    # 5. Perform the transfer
    # Clear group_name for old owner
    old_owner.group_name = None
    await add_obj(old_owner, db=db) # add_obj commits changes

    # Assign group_name to new owner
    new_owner.group_name = current_group_name
    await add_obj(new_owner, db=db) # add_obj commits changes

    return f"Success: Group '{current_group_name}' ownership transferred from @{old_owner.username} to @{new_owner.username}."
