from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SightingCreate(BaseModel):
    species: str = Field(min_length=1, max_length=100)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    observed_at: datetime

    photo_url: HttpUrl | None = None

    notes: str | None = None


class SightingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    species: str
    latitude: float
    longitude: float
    observed_at: datetime
    photo_url: HttpUrl | None
    notes: str | None
    created_at: datetime