from sqlalchemy import select, update
from schemas import UserCreate, User, UserUpdate
from db import SessionLocal
from models import User

async def get_user_by_telegram_id(telegram_id: int, db: SessionLocal = None):
    try:
        if db is None:
            async with SessionLocal() as db:
                select_stmt = select(User).where(User.telegram_id == telegram_id)
                db_user = await db.execute(select_stmt)
                return db_user.scalar()
        else:
            select_stmt = select(User).where(User.telegram_id == telegram_id)
            db_user = await db.execute(select_stmt)
            return db_user.scalar()
    except Exception as e:
        raise e

async def create_user(user: UserCreate, db: SessionLocal = None):
    existing_user = await get_user_by_telegram_id(user.telegram_id, db)
    if existing_user is not None:
        return existing_user
    db_user = User(**user.model_dump())
    try :
        if db is None:
            async with SessionLocal() as db:
                db.add(db_user)
                await db.commit()
                await db.refresh(db_user)
        else:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
        return db_user
    except Exception as e:
        raise e

async def update_user(telegram_id: int, user: UserUpdate, db: SessionLocal = None):
    try:
        if db is None:
            async with SessionLocal() as db:
                existing_user = await get_user_by_telegram_id(telegram_id, db)
                if existing_user is None:
                    return None
                db_user = existing_user 
                user = user.model_dump(exclude_unset=True)
                update_stmt = update(User).where(User.telegram_id == telegram_id).values(user)
                await db.execute(update_stmt)
                await db.commit()
                await db.refresh(db_user)
        else:
            existing_user = await get_user_by_telegram_id(telegram_id, db)
            if existing_user is None:
                return None
            db_user = existing_user
            user = user.model_dump(exclude_unset=True)
            update_stmt = update(User).where(User.telegram_id == telegram_id).values(user)
            await db.execute(update_stmt)
            await db.commit()
            await db.refresh(db_user)

        return db_user
    except Exception as e:
        raise e

async def delete_user(telegram_id: int, db: SessionLocal = None):
    try:
        if db is None:
            async with SessionLocal() as db:
                db_user = await get_user_by_telegram_id(telegram_id, db)
                await db.delete(db_user)
                await db.commit()
                return True
        else:
            db_user = await get_user_by_telegram_id(telegram_id, db)
            await db.delete(db_user)
            await db.commit()
            return True
    except Exception as e:
        raise e
