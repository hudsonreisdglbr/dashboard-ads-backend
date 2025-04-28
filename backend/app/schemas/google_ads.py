from pydantic import BaseModel
from typing import Optional

# Propriedades compartilhadas
class GoogleAdsAccountBase(BaseModel):
    account_id: Optional[str] = None
    name: Optional[str] = None

# Propriedades para receber na criação/atualização
class GoogleAdsAccountCreate(GoogleAdsAccountBase):
    account_id: str
    name: str
    refresh_token: str # Recebido via OAuth
    user_id: int

class GoogleAdsAccountUpdate(GoogleAdsAccountBase):
    refresh_token: Optional[str] = None

# Propriedades armazenadas no DB
class GoogleAdsAccountInDBBase(GoogleAdsAccountBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Propriedades para retornar ao cliente (sem refresh token)
class GoogleAdsAccount(GoogleAdsAccountInDBBase):
    pass

# Propriedades completas no DB
class GoogleAdsAccountInDB(GoogleAdsAccountInDBBase):
    refresh_token: str
