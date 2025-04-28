from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.routes import auth
from app.core.config import settings
from app.services.meta_ads_service import MetaAdsService

router = APIRouter()

def get_meta_ads_service(
    db: Session = Depends(auth.get_db),
    account_id: int = None,
    current_user: models.User = Depends(auth.get_current_active_user)
) -> MetaAdsService:
    """
    Cria uma instância do serviço Meta Ads com as credenciais apropriadas
    """
    # Se account_id for fornecido, usar as credenciais dessa conta específica
    if account_id:
        account = crud.crud_meta_ads.get_meta_ads_account(db, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Conta Meta Ads não encontrada")
        
        # Verificar se o usuário tem acesso a esta conta
        if account.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
            raise HTTPException(status_code=403, detail="Sem permissão para acessar esta conta")
        
        access_token = account.access_token
    else:
        # Caso contrário, usar um token padrão (para testes ou admin)
        access_token = settings.META_ACCESS_TOKEN
    
    try:
        return MetaAdsService(
            app_id=settings.META_APP_ID,
            app_secret=settings.META_APP_SECRET,
            access_token=access_token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar serviço Meta Ads: {str(e)}")

@router.get("/accounts", response_model=List[schemas.MetaAdsAccount])
def read_meta_ads_accounts(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Retorna todas as contas Meta Ads do usuário atual
    """
    if crud.crud_user.is_admin(current_user):
        # Administradores podem ver todas as contas
        accounts = db.query(models.MetaAdsAccount).all()
    else:
        # Usuários normais só veem suas próprias contas
        accounts = crud.crud_meta_ads.get_meta_ads_accounts_by_user(db, current_user.id)
    
    return accounts

@router.post("/accounts", response_model=schemas.MetaAdsAccount)
def create_meta_ads_account(
    *,
    db: Session = Depends(auth.get_db),
    account_in: schemas.MetaAdsAccountCreate,
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Cria uma nova conta Meta Ads
    """
    # Verificar se o usuário tem permissão para criar conta para o user_id especificado
    if account_in.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para criar conta para outro usuário"
        )
    
    # Verificar se já existe uma conta com este account_id
    existing_account = db.query(models.MetaAdsAccount).filter(
        models.MetaAdsAccount.account_id == account_in.account_id
    ).first()
    
    if existing_account:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma conta com este ID"
        )
    
    account = crud.crud_meta_ads.create_meta_ads_account(db=db, account_in=account_in)
    return account

@router.get("/campaigns/{account_id}")
def read_meta_ads_campaigns(
    account_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Retorna as campanhas do Meta Ads para uma conta específica
    """
    # Obter a conta do banco de dados
    account = crud.crud_meta_ads.get_meta_ads_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Conta Meta Ads não encontrada")
    
    # Verificar permissões
    if account.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para acessar esta conta"
        )
    
    # Inicializar o serviço e obter as campanhas
    try:
        service = get_meta_ads_service(db, account_id, current_user)
        campaigns = service.get_campaigns(account.account_id)
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter campanhas: {str(e)}"
        )

@router.get("/ads/{account_id}")
@router.get("/ads/{account_id}/{campaign_id}")
def read_meta_ads_ads(
    account_id: int,
    campaign_id: str = None, # Opcional
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Retorna os anúncios do Meta Ads para uma conta ou campanha específica
    """
    # Obter a conta do banco de dados
    account = crud.crud_meta_ads.get_meta_ads_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Conta Meta Ads não encontrada")
    
    # Verificar permissões
    if account.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para acessar esta conta"
        )
    
    # Inicializar o serviço e obter os anúncios
    try:
        service = get_meta_ads_service(db, account_id, current_user)
        ads = service.get_ads(account.account_id, campaign_id)
        return ads
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter anúncios: {str(e)}"
        )
