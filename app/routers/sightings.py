from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Sighting
from app.schemas import SightingCreate, SightingResponse

router = APIRouter()

@router.post("/sightings", response_model=SightingResponse, status_code=status.HTTP_201_CREATED)
def create_sighting(payload: SightingCreate, db: Session = Depends(get_db)):
    sighting = Sighting(**payload.model_dump(mode="json"))
    db.add(sighting)
    db.commit()
    db.refresh(sighting)
    return sighting

@router.get("/sightings", response_model=list[SightingResponse])
def list_sightings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Sighting).offset(skip).limit(min(limit, 500)).all()

@router.get("/sightings/{sighting_id}", response_model=SightingResponse)
def get_sighting(sighting_id: int, db: Session = Depends(get_db)):
    sighting = db.get(Sighting, sighting_id)
    if sighting is None:
        raise HTTPException(status_code=404, detail="Sighting not found")
    return sighting