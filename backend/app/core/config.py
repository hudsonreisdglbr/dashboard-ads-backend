from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Dashboard de Performance Digital"
    
    # Configurações do banco de dados
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "dashboard_ads"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Configurações de segurança
    SECRET_KEY: str = "sua_chave_secreta_aqui"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    
    # Configurações do Google Ads
    GOOGLE_ADS_CLIENT_ID: Optional[str] = None
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = None
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = None
    GOOGLE_ADS_REFRESH_TOKEN: Optional[str] = None
    
    # Configurações do Meta Ads (Facebook)
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    META_ACCESS_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.SQLALCHEMY_DATABASE_URI and self.POSTGRES_DB:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )


settings = Settings()
