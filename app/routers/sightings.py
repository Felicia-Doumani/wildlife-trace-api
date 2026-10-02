from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime
from app.database import get_db
from app.models import Sighting
from app.schemas import SightingCreate, SightingResponse, SightingUpdate
from app.workers.tasks import process_sighting

router = APIRouter()

@router.post("/sightings", response_model=SightingResponse, status_code=status.HTTP_201_CREATED)
def create_sighting(payload: SightingCreate, db: Session = Depends(get_db)):
    sighting = Sighting(**payload.model_dump(mode="json"))
    db.add(sighting)
    db.commit()
    db.refresh(sighting)
    process_sighting.delay(sighting.id)
    return sighting

@router.get("/sightings", response_model=list[SightingResponse])
def list_sightings(
    skip: int = 0,
    limit: int = 100,
    species: str | None = None,
    observed_from: datetime | None = None,
    observed_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Sighting)

    if species:
        query = query.filter(Sighting.species.ilike(f"%{species}%"))

    if observed_from:
        query = query.filter(Sighting.observed_at >= observed_from)

    if observed_to:
        query = query.filter(Sighting.observed_at <= observed_to)

    return query.offset(skip).limit(min(limit, 500)).all()

@router.get("/sightings/{sighting_id}", response_model=SightingResponse)
def get_sighting(sighting_id: int, db: Session = Depends(get_db)):
    sighting = db.get(Sighting, sighting_id)
    if sighting is None:
        raise HTTPException(status_code=404, detail="Sighting not found")
    return sighting

@router.patch("/sightings/{sighting_id}", response_model=SightingResponse)
def update_sighting(
    sighting_id: int,
    payload: SightingUpdate,
    db: Session = Depends(get_db),
):
    sighting = db.get(Sighting, sighting_id)

    if sighting is None:
        raise HTTPException(status_code=404, detail="Sighting not found")

    update_data = payload.model_dump(
        exclude_unset=True,
        mode="json",
    )

    for field, value in update_data.items():
        setattr(sighting, field, value)

    db.commit()
    db.refresh(sighting)

    return sighting

@router.delete(
    "/sightings/{sighting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sighting(
    sighting_id: int,
    db: Session = Depends(get_db),
):
    sighting = db.get(Sighting, sighting_id)

    if sighting is None:
        raise HTTPException(status_code=404, detail="Sighting not found")

    db.delete(sighting)
    db.commit()