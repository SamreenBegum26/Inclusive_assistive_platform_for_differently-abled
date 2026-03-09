from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.schemes.models import GovernmentScheme
from app.modules.schemes.schemas import SchemeResponse, SchemeCreate

router = APIRouter()


# GET ALL SCHEMES
@router.get("/", response_model=List[SchemeResponse])
def get_all_schemes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(GovernmentScheme).all()


# GET SCHEMES BY DISABILITY TYPE
@router.get("/filter", response_model=List[SchemeResponse])
def get_schemes_by_disability(
    disability_type: str = Query(..., description="physical / visual / hearing / mental"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    valid_types = ["physical", "visual", "hearing", "mental"]
    if disability_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid disability type. Choose from: {valid_types}"
        )

    schemes = db.query(GovernmentScheme).filter(
        GovernmentScheme.disability_type.in_([disability_type, "all"])
    ).all()

    if not schemes:
        raise HTTPException(status_code=404, detail=f"No schemes found for: {disability_type}")

    return schemes


# GET SINGLE SCHEME
@router.get("/{scheme_id}", response_model=SchemeResponse)
def get_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    scheme = db.query(GovernmentScheme).filter(GovernmentScheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme


# ADD SCHEME (ADMIN ONLY)
@router.post("/", response_model=SchemeResponse)
def add_scheme(
    payload: SchemeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add schemes")

    valid_types = ["physical", "visual", "hearing", "mental", "all"]
    if payload.disability_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid disability type. Choose from: {valid_types}")

    new_scheme = GovernmentScheme(**payload.dict())
    db.add(new_scheme)
    db.commit()
    db.refresh(new_scheme)
    return new_scheme


# DELETE SCHEME (ADMIN ONLY)
@router.delete("/{scheme_id}")
def delete_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete schemes")

    scheme = db.query(GovernmentScheme).filter(GovernmentScheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    db.delete(scheme)
    db.commit()
    return {"message": "Scheme deleted successfully"}