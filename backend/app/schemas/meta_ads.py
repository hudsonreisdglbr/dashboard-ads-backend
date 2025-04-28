from pydantic import BaseModel
from typing import Optional

# Propriedades compartilhadas
class MetaAdsAccountBase(BaseModel):
    account_id: Optional[str] = None
    name: Optional[str] = None

# Propriedades para receber na criação/atualização
class MetaAdsAccountCreate(MetaAdsAccountBase):
    account_id: str
    name: str
    access_token: str # Recebido via Facebook Login
    user_id: int

class MetaAdsAccountUpdate(MetaAdsAccountBase):
    access_token: Optional[str] = None

# Propriedades armazenadas no DB
class MetaAdsAccountInDBBase(MetaAdsAccountBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Propriedades para retornar ao cliente (sem access token)
class MetaAdsAccount(MetaAdsAccountInDBBase):
    pass

# Propriedades completas no DB
class MetaAdsAccountInDB(MetaAdsAccountInDBBase):
    access_token: str
