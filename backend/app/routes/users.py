from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.routes import auth

router = APIRouter()


@router.post("/", response_model=schemas.user.User)
def create_user(
    *, 
    db: Session = Depends(auth.get_db), 
    user_in: schemas.user.UserCreate,
    current_user: models.User = Depends(auth.get_current_active_admin) # Apenas admin pode criar usuários
) -> Any:
    """
    Cria um novo usuário.
    """
    user = crud.crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com este email.",
        )
    user = crud.crud_user.create_user(db=db, user_in=user_in)
    return user


@router.get("/me", response_model=schemas.user.User)
def read_user_me(
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Obtém o usuário atual.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.user.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db),
) -> Any:
    """
    Obtém um usuário pelo ID.
    """
    user = crud.crud_user.get_user(db, user_id=user_id)
    if user == current_user or crud.crud_user.is_admin(current_user):
        return user
    raise HTTPException(
        status_code=403,
        detail="O usuário não tem permissões suficientes"
    )


@router.get("/", response_model=List[schemas.user.User])
def read_users(
    db: Session = Depends(auth.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_admin) # Apenas admin pode listar todos os usuários
) -> Any:
    """
    Obtém uma lista de usuários.
    """
    users = crud.crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.put("/{user_id}", response_model=schemas.user.User)
def update_user(
    *,
    db: Session = Depends(auth.get_db),
    user_id: int,
    user_in: schemas.user.UserUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Atualiza um usuário.
    """
    user = crud.crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="O usuário com este ID não foi encontrado.",
        )
    # Apenas admin ou o próprio usuário podem atualizar
    if not crud.crud_user.is_admin(current_user) and user.id != current_user.id:
         raise HTTPException(
            status_code=403,
            detail="O usuário não tem permissões suficientes"
        )
    user = crud.crud_user.update_user(db=db, db_user=user, user_in=user_in)
    return user
