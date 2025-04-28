from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.models import MetaAdsAccount
from app.schemas.meta_ads import MetaAdsAccountCreate, MetaAdsAccountUpdate


def get_meta_ads_account(db: Session, account_id: int) -> Optional[MetaAdsAccount]:
    return db.query(MetaAdsAccount).filter(MetaAdsAccount.id == account_id).first()


def get_meta_ads_accounts_by_user(db: Session, user_id: int) -> List[MetaAdsAccount]:
    return db.query(MetaAdsAccount).filter(MetaAdsAccount.user_id == user_id).all()


def create_meta_ads_account(db: Session, account_in: MetaAdsAccountCreate) -> MetaAdsAccount:
    db_account = MetaAdsAccount(
        account_id=account_in.account_id,
        name=account_in.name,
        access_token=account_in.access_token,
        user_id=account_in.user_id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def update_meta_ads_account(
    db: Session, *, db_account: MetaAdsAccount, account_in: MetaAdsAccountUpdate
) -> MetaAdsAccount:
    update_data = account_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def delete_meta_ads_account(db: Session, account_id: int) -> Optional[MetaAdsAccount]:
    db_account = get_meta_ads_account(db, account_id)
    if db_account:
        db.delete(db_account)
        db.commit()
    return db_account
