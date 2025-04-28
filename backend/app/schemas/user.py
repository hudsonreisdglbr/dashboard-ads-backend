from pydantic import BaseModel
from typing import Optional


# Propriedades compartilhadas
class UserBase(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: bool = False
    name: Optional[str] = None


# Propriedades para receber na criação do usuário
class UserCreate(UserBase):
    email: str
    password: str
    name: str


# Propriedades para receber na atualização do usuário
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Propriedades adicionais armazenadas no DB
class UserInDB(UserInDBBase):
    hashed_password: str


# Propriedades adicionais para retornar ao cliente
class User(UserInDBBase):
    pass

# --- Schemas para Token ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

