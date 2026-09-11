# backend/app/models/layout_models.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Screen(BaseModel):
    """
    One screen in the stadium.
    """
    id: str
    zone_id: str
    row: int
    col: int

    # Screen type (e.g. glassfloor_tile, surrounding_banner, megatron_panel)
    screen_type: str = "generic"

    # Optional tags (e.g. ["premium", "vip_side"])
    tags: List[str] = []

    # Free-form metadata for future use
    metadata: Dict[str, Any] = {}


class Zone(BaseModel):
    """
    A zone of the stadium (GlassFloor, Surrounding, Megatron).
    """
    id: str
    name: str
    description: str
    rows: int
    cols: int
    screens: List[Screen]


class MultiIndexKey(BaseModel):
    """
    Multi-dimensional key for querying screens.

    Combines:
    - zone_id
    - 2D position (x, y) on the grid
    - screen type (screen_type)
    - advertisement category (ad_category)
    - time window (time_window)
    """

    screen_id: str
    zone_id: str
    x: float
    y: float
    screen_type: str

    # Optional "logical" dimensions
    ad_category: Optional[str] = None     # e.g. "tech", "sports"
    time_window: Optional[str] = None     # e.g. "prime_time", "halftime"

    @classmethod
    def from_screen(
        cls,
        screen: Screen,
        ad_category: Optional[str] = None,
        time_window: Optional[str] = None,
    ) -> "MultiIndexKey":
        """
        Builds a MultiIndexKey from a Screen plus the logical dimensions.

        For now:
        - x = col
        - y = row
        """
        return cls(
            screen_id=screen.id,
            zone_id=screen.zone_id,
            x=float(screen.col),
            y=float(screen.row),
            screen_type=screen.screen_type,
            ad_category=ad_category,
            time_window=time_window,
        )


class DistributedResult(BaseModel):
    """
    A result from the DistributedScreenIndex.
    Includes which node returned this screen.
    """
    screen: Screen
    distance: float
    node: str  # "node_glassfloor" | "node_surrounding" | "node_megatron"


class ScreenRecommendation(BaseModel):
    """
    A recommendation result:
    - which screen was chosen
    - with which attributes
    - how far it is from the target point
    """
    screen_id: str
    zone_id: str
    x: float
    y: float
    screen_type: str
    ad_category: Optional[str] = None
    time_window: Optional[str] = None
    distance: float
