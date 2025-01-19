from sqlalchemy import Column, DateTime, String, text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String, nullable=False, unique=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    access_token = Column(String, nullable=False, unique=True)
    access_token_expires_at = Column(DateTime, nullable=False)
    email_verified_at = Column(DateTime, nullable=False, server_default=text("now()"))
    created_at = Column(DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()"))