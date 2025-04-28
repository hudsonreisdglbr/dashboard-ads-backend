from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.routes import auth
from app.core.config import settings
from app.services.google_ads_service import GoogleAdsService

router = APIRouter()

def get_google_ads_service(
    db: Session = Depends(auth.get_db),
    account_id: int = None,
    current_user: models.User = Depends(auth.get_current_active_user)
) -> GoogleAdsService:
    """
    Cria uma instância do serviço Google Ads com as credenciais apropriadas
    """
    # Se account_id for fornecido, usar as credenciais dessa conta específica
    if account_id:
        account = crud.crud_google_ads.get_google_ads_account(db, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Conta Google Ads não encontrada")
        
        # Verificar se o usuário tem acesso a esta conta
        if account.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
            raise HTTPException(status_code=403, detail="Sem permissão para acessar esta conta")
        
        refresh_token = account.refresh_token
    else:
        # Caso contrário, usar um token padrão (para testes ou admin)
        refresh_token = settings.GOOGLE_ADS_REFRESH_TOKEN
    
    try:
        return GoogleAdsService(
            client_id=settings.GOOGLE_ADS_CLIENT_ID,
            client_secret=settings.GOOGLE_ADS_CLIENT_SECRET,
            developer_token=settings.GOOGLE_ADS_DEVELOPER_TOKEN,
            refresh_token=refresh_token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar serviço Google Ads: {str(e)}")

@router.get("/accounts", response_model=List[schemas.GoogleAdsAccount])
def read_google_ads_accounts(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Retorna todas as contas Google Ads do usuário atual
    """
    if crud.crud_user.is_admin(current_user):
        # Administradores podem ver todas as contas
        accounts = db.query(models.GoogleAdsAccount).all()
    else:
        # Usuários normais só veem suas próprias contas
        accounts = crud.crud_google_ads.get_google_ads_accounts_by_user(db, current_user.id)
    
    return accounts

@router.post("/accounts", response_model=schemas.GoogleAdsAccount)
def create_google_ads_account(
    *,
    db: Session = Depends(auth.get_db),
    account_in: schemas.GoogleAdsAccountCreate,
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Cria uma nova conta Google Ads
    """
    # Verificar se o usuário tem permissão para criar conta para o user_id especificado
    if account_in.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para criar conta para outro usuário"
        )
    
    # Verificar se já existe uma conta com este account_id
    existing_account = db.query(models.GoogleAdsAccount).filter(
        models.GoogleAdsAccount.account_id == account_in.account_id
    ).first()
    
    if existing_account:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma conta com este ID"
        )
    
    account = crud.crud_google_ads.create_google_ads_account(db=db, account_in=account_in)
    return account

@router.get("/campaigns/{account_id}")
def read_google_ads_campaigns(
    account_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Retorna as campanhas do Google Ads para uma conta específica
    """
    # Obter a conta do banco de dados
    account = crud.crud_google_ads.get_google_ads_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Conta Google Ads não encontrada")
    
    # Verificar permissões
    if account.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para acessar esta conta"
        )
    
    # Inicializar o serviço e obter as campanhas
    try:
        service = get_google_ads_service(db, account_id, current_user)
        campaigns = service.get_campaigns(account.account_id)
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter campanhas: {str(e)}"
        )

@router.get("/ads/{account_id}/{campaign_id}")
def read_google_ads_ads(
    account_id: int,
    campaign_id: str,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Retorna os anúncios do Google Ads para uma campanha específica
    """
    # Obter a conta do banco de dados
    account = crud.crud_google_ads.get_google_ads_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Conta Google Ads não encontrada")
    
    # Verificar permissões
    if account.user_id != current_user.id and not crud.crud_user.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para acessar esta conta"
        )
    
    # Inicializar o serviço e obter os anúncios
    try:
        service = get_google_ads_service(db, account_id, current_user)
        
        # Primeiro, obter os grupos de anúncios da campanha
        ad_groups = service.get_ad_groups(account.account_id, campaign_id)
        
        # Depois, obter os anúncios para cada grupo
        all_ads = []
        for ad_group in ad_groups:
            ads = service.get_ads(account.account_id, ad_group["id"])
            # Adicionar informação do grupo de anúncios a cada anúncio
            for ad in ads:
                ad["ad_group"] = ad_group["name"]
            all_ads.extend(ads)
        
        return all_ads
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter anúncios: {str(e)}"
        )
