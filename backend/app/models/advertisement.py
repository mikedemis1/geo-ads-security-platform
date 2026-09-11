# backend/app/models/advertisement.py
from pydantic import BaseModel


class Advertisement(BaseModel):
    """
    Advertisement model, as stored in the database:
    id, name, image_url, zone.
    """

    id: int
    name: str
    image_url: str | None = None
    zone: str
