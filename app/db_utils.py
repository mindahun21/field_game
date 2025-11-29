"""
This module provides asynchronous utility functions for interacting with the database
using SQLAlchemy, specifically for User and Role management.
"""

from typing import Tuple, TypeVar, Union, Literal,List
from sqlalchemy import select

from .models import Role,User

T = TypeVar("T")

async def add_obj(obj, db=None):
    """
    Adds an object to the database, commits the transaction, and refreshes the object.

    Args:
        obj: The SQLAlchemy model instance to add.
        db: The SQLAlchemy session.

    Returns:
        The added and refreshed object.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj

async def delete_obj(obj, db=None):
    """
    Deletes an object from the database and commits the transaction.

    Args:
        obj: The SQLAlchemy model instance to delete.
        db: The SQLAlchemy session.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    db.delete(obj)
    db.commit()

async def delete_all_rows(model, db=None):
    """
    Deletes all rows from a specified model's table and commits the transaction.

    Args:
        model: The SQLAlchemy model class from which to delete all rows.
        db: The SQLAlchemy session.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")

    rows = db.query(model).all()
    for row in rows:
        db.delete(row)

    db.commit()

async def set_val(obj, db=None, **kwargs):
    """
    Sets specified attributes on an object, adds it to the database, and commits the transaction.

    Args:
        obj: The SQLAlchemy model instance to update.
        db: The SQLAlchemy session.
        **kwargs: Keyword arguments representing attribute-value pairs to set.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    for k, v in kwargs.items():
        setattr(obj, k, v)
    
    db.add(obj)
    db.commit()

async def add_entry(obj:T, db=None, **kwargs) -> T:
    """
    Creates a new entry for a given model, adds it to the database, and commits the transaction.

    Args:
        obj: The SQLAlchemy model class for the new entry.
        db: The SQLAlchemy session.
        **kwargs: Keyword arguments for initializing the new model instance.

    Returns:
        The newly created and added model instance.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    new_entry = obj(**kwargs)
    db.add(new_entry)
    db.commit()

    return new_entry

async def remove_entry(obj, db=None, **filters):
    """
    Removes a single entry from the database based on filters and commits the transaction.

    Args:
        obj: The SQLAlchemy model class to query.
        db: The SQLAlchemy session.
        **filters: Keyword arguments for filtering the entry to remove.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")

    stmt = select(obj).filter_by(**filters)
    entry = db.scalars(stmt).first()
    if entry: # Ensure entry exists before deleting
        db.delete(entry)
        db.commit()

async def get_entry(obj, db=None, **filters) -> Union[T, Literal[False]]:
    """
    Retrieves a single entry from the database based on filters.

    Args:
        obj: The SQLAlchemy model class to query.
        db: The SQLAlchemy session.
        **filters: Keyword arguments for filtering the entry.

    Returns:
        The found model instance, or False if no entry is found.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    stmt = select(obj).filter_by(**filters)
    entry = db.scalars(stmt).first()
    if entry:
        return entry
    
    return False

async def get_entries(obj, db=None, **filters) -> Union[List[T], Literal[False]]:
    """
    Retrieves multiple entries from the database based on filters.

    Args:
        obj: The SQLAlchemy model class to query.
        db: The SQLAlchemy session.
        **filters: Keyword arguments for filtering the entries.

    Returns:
        A list of found model instances, or False if no entries are found.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    stmt = select(obj).filter_by(**filters)
    entries = db.scalars(stmt).all()
    if entries:
        return entries
    
    return False

async def is_group_name_taken(group_name: str, db=None) -> bool:
    """
    Checks if a given group name is already taken by another user.

    Args:
        group_name: The group name to check.
        db: The SQLAlchemy session.

    Returns:
        True if the group name is taken, False otherwise.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    user = await get_entry(User, db=db, group_name=group_name)
    return user is not False

async def get_role(user_id: int, db=None) -> Tuple[Role, Union[User, None]]:
    """
    Retrieves the role and User object for a given user ID.

    Args:
        user_id: The ID of the user.
        db: The SQLAlchemy session.

    Returns:
        A tuple containing the user's Role enum and their User object (or None if not found).

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        raise ValueError("Database connection not provided.")
    
    user = await get_entry(User, db=db, user_id=user_id)

    if user and user.role == Role.USER:
        return (Role.USER, user)
    elif user and user.role == Role.ADMIN:
        return (Role.ADMIN, user)
    elif user and user.role == Role.GAME_ADMIN:
        return (Role.GAME_ADMIN, user)
    
    return (Role.NONE, None)

async def transfer_group_ownership(current_group_name: str, new_owner_username: str, db=None) -> str:
    """
    Transfers ownership of an existing group from its current owner to a new user.

    Args:
        current_group_name: The name of the group whose ownership is to be transferred.
        new_owner_username: The username of the user who will become the new owner.
        db: The SQLAlchemy session.

    Returns:
        A string indicating the success or failure of the transfer operation.

    Raises:
        ValueError: If no database connection is provided.
    """
    if db is None:
        return "Error: Database connection not provided."

    old_owner = await get_entry(User, db=db, group_name=current_group_name)
    if not old_owner:
        return f"Error: No group found with name '{current_group_name}'."
    
    new_owner = await get_entry(User, db=db, username=new_owner_username)
    if not new_owner:
        return f"Error: New owner user @{new_owner_username} not found."
    
    if new_owner.group_name:
        return f"Error: New owner @{new_owner_username} already owns group '{new_owner.group_name}'. Cannot transfer."
    
    if old_owner.user_id == new_owner.user_id:
        return f"Error: User @{new_owner_username} is already the owner of group '{current_group_name}'."

    # Perform the transfer
    old_owner.group_name = None
    await add_obj(old_owner, db=db) 

    new_owner.group_name = current_group_name
    await add_obj(new_owner, db=db) 

    return f"Success: Group '{current_group_name}' ownership transferred from @{old_owner.username} to @{new_owner.username}."