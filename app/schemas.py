from pydantic import BaseModel, Field
from datetime import datetime
from pydantic.types import conint
from typing import Optional
from uuid import UUID


class User(BaseModel):
    id: UUID
    email: str
    telegram_id: int
    access_token: str
    access_token_expires_at: datetime
    email_verified_at: datetime

    model_config = {
        "arbitrary_types_allowed": True,
    }

class UserCreate(BaseModel):
    email: str
    telegram_id: int
    access_token: str
    access_token_expires_at: datetime

    model_config = {
        "arbitrary_types_allowed": True,
    }

class UserUpdate(BaseModel):
    email: Optional[str]
    telegram_id: Optional[int]
    access_token: Optional[str]
    access_token_expires_at: Optional[datetime]
    email_verified_at: Optional[datetime]

    model_config = {
        "arbitrary_types_allowed": True,
    }