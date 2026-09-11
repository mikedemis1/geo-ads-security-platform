# backend/app/models/placement_models.py

from datetime import datetime
from pydantic import BaseModel


class AdPlacement(BaseModel):
    """
    An active placement:
    - which advertisement (ad_id)
    - on which screen (screen_id, zone_id)
    - with which multi-index attributes
    - when it was assigned (assigned_at)
    """

    ad_id: int
    screen_id: str
    zone_id: str

    x: float
    y: float

    screen_type: str | None = None
    ad_category: str | None = None
    time_window: str | None = None

    assigned_at: datetime
