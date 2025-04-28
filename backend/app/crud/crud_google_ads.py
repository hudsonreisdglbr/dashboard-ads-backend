from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.models import GoogleAdsAccount
from app.schemas.google_ads import GoogleAdsAccountCreate, GoogleAdsAccountUpdate


def get_google_ads_account(db: Session, account_id: int) -> Optional[GoogleAdsAccount]:
    return db.query(GoogleAdsAccount).filter(GoogleAdsAccount.id == account_id).first()


def get_google_ads_accounts_by_user(db: Session, user_id: int) -> List[GoogleAdsAccount]:
    return db.query(GoogleAdsAccount).filter(GoogleAdsAccount.user_id == user_id).all()


def create_google_ads_account(db: Session, account_in: GoogleAdsAccountCreate) -> GoogleAdsAccount:
    db_account = GoogleAdsAccount(
        account_id=account_in.account_id,
        name=account_in.name,
        refresh_token=account_in.refresh_token,
        user_id=account_in.user_id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def update_google_ads_account(
    db: Session, *, db_account: GoogleAdsAccount, account_in: GoogleAdsAccountUpdate
) -> GoogleAdsAccount:
    update_data = account_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def delete_google_ads_account(db: Session, account_id: int) -> Optional[GoogleAdsAccount]:
    db_account = get_google_ads_account(db, account_id)
    if db_account:
        db.delete(db_account)
        db.commit()
    return db_account
