# backend/app/services/placement_service.py

from datetime import datetime
from typing import List

from app.models.placement_models import AdPlacement
from app.models.layout_models import MultiIndexKey


class PlacementService:
    """
    A simple in-memory table of placements.
    Never touches the database; everything lives in the backend's memory.
    """

    _placements: List[AdPlacement] = []

    @classmethod
    def assign_ad(cls, ad_id: int, key: MultiIndexKey) -> AdPlacement:
        """
        Create a new placement of an advertisement on a screen,
        store it and return it.
        """
        placement = AdPlacement(
            ad_id=ad_id,
            screen_id=key.screen_id,
            zone_id=key.zone_id,
            x=key.x,
            y=key.y,
            screen_type=key.screen_type,
            ad_category=key.ad_category,
            time_window=key.time_window,
            assigned_at=datetime.utcnow(),
        )
        cls._placements.append(placement)
        return placement

    @classmethod
    def list_all(cls) -> List[AdPlacement]:
        """Return every placement."""
        return list(cls._placements)

    @classmethod
    def list_by_screen(cls, screen_id: str) -> List[AdPlacement]:
        """Return the placements for one screen."""
        return [p for p in cls._placements if p.screen_id == screen_id]
