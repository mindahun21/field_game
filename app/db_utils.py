
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

async def get_role(chat_id:int,db=None) -> Tuple[Role,Union[User, None]]:
    if db is None:
        raise ValueError("you didn't pass database connection to the function")
    
    user = await get_entry(User,db=db,chat_id=chat_id)

    if user and user.role == "user":
        return (Role.USER,user)
    elif user and user.role == "admin":
        return (Role.ADMIN,user)
    
    return (Role.NONE,None)
