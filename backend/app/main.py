from fastapi import FastAPI

from app.core.config import settings
# Importar rotas aqui quando forem criadas
from app.routes import users, auth, google_ads, meta_ads #, campaigns

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Incluir roteadores aqui
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(google_ads.router, prefix=f"{settings.API_V1_STR}/google-ads", tags=["google-ads"])
app.include_router(meta_ads.router, prefix=f"{settings.API_V1_STR}/meta-ads", tags=["meta-ads"])
# app.include_router(campaigns.router, prefix=f"{settings.API_V1_STR}/campaigns", tags=["campaigns"])

@app.get("/")
async def root():
    return {"message": f"Bem-vindo ao {settings.PROJECT_NAME}"}

# Adicionar inicialização do banco de dados (opcional, pode ser feito via Alembic)
# from app.db import base
# from app.db.session import engine
# base.Base.metadata.create_all(bind=engine)