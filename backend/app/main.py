# backend/app/main.py

import os
import time
import json
import logging

from dotenv import load_dotenv
# app/main.py είναι σε backend/app/ → το .env είναι ένα επίπεδο πάνω (backend/)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware


from app.services.advertisement_service import AdvertisementService
from app.models.advertisement import Advertisement
from app.services.layout_service import LayoutService, get_screen_index, DistributedScreenIndex
from app.models.layout_models import Zone, Screen, MultiIndexKey, ScreenRecommendation, DistributedResult
from app.websockets.websockets import router as websocket_router, ws_manager
from app.models.placement_models import AdPlacement
from app.services.placement_service import PlacementService
from app.security.deps import require_scope
from app.security.auth_routes import router as auth_router, limiter as auth_limiter

app = FastAPI(title="Geo-Ads Backend")

# ── Rate Limiting ──────────────────────────────────────
app.state.limiter = auth_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Security Headers Middleware ────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' ws://localhost:* wss://localhost:*"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# ── Audit Logger ──────────────────────────────────────
audit_logger = logging.getLogger("audit")
audit_handler = logging.FileHandler("audit.log", encoding="utf-8")
audit_handler.setFormatter(logging.Formatter("%(message)s"))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)


@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start = time.time()

    sub = "anonymous"
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        try:
            from app.security.jwt_service import decode_and_verify
            token = auth_header.split()[1]
            payload = decode_and_verify(token)
            sub = payload.get("sub", "unknown")
        except Exception:
            sub = "invalid_token"

    response = await call_next(request)

    ms = round((time.time() - start) * 1000, 2)
    log_entry = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": request.method,
        "path": request.url.path,
        "sub": sub,
        "status": response.status_code,
        "ms": ms,
    }
    audit_logger.info(json.dumps(log_entry, ensure_ascii=False))

    # Record rate-limited events to threat engine
    if response.status_code == 429:
        try:
            from app.security.threat_engine import get_threat_engine
            engine = get_threat_engine()
            ip = request.client.host if request.client else "unknown"
            engine.record_event(
                event_type="rate_limited",
                source_ip=ip,
                details={"path": request.url.path, "method": request.method},
            )
        except Exception:
            pass

    return response


# ── Health ─────────────────────────────────────────────
@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ── CORS ───────────────────────────────────────────────
_RAW_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8080"
)
ALLOWED_ORIGINS = [o.strip() for o in _RAW_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Secret"],
)

app.include_router(websocket_router)
app.include_router(auth_router)

# ── Distributed Index Singleton ────────────────────────────────────────────
_DIST_INDEX: DistributedScreenIndex | None = None


def get_distributed_index() -> DistributedScreenIndex:
    global _DIST_INDEX
    if _DIST_INDEX is None:
        zones = LayoutService.get_layout()
        _DIST_INDEX = DistributedScreenIndex(zones)
    return _DIST_INDEX


@app.get("/")
def root():
    return {"message": "Geo-Ads backend is running"}


# ── ΔΙΑΦΗΜΙΣΕΙΣ ────────────────────────────────────────
@app.get(
    "/advertisements",
    response_model=list[Advertisement],
    dependencies=[Depends(require_scope(["ads:read"]))],
)
def list_advertisements():
    return AdvertisementService.get_all()


@app.get(
    "/advertisements/zone/{zone_id}",
    response_model=list[Advertisement],
    dependencies=[Depends(require_scope(["ads:read"]))],
)
def list_advertisements_by_zone(zone_id: str):
    return AdvertisementService.get_by_zone(zone_id)


# ── LAYOUT ─────────────────────────────────────────────
@app.get(
    "/layout",
    response_model=list[Zone],
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def get_layout():
    return LayoutService.get_layout()


@app.get(
    "/layout/zones/{zone_id}/screens",
    response_model=list[Screen],
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def get_screens_by_zone(zone_id: str):
    index = get_screen_index()
    return index.query_by_zone(zone_id)


@app.get(
    "/layout/zones/{zone_id}/screens/{row}/{col}",
    response_model=Screen,
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def get_screen_by_grid(zone_id: str, row: int, col: int):
    index = get_screen_index()
    screen = index.query_by_grid(zone_id, row, col)
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found")
    return screen


@app.get(
    "/layout/query/near",
    response_model=list[Screen],
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def query_screens_near(
    x: float = Query(...),
    y: float = Query(...),
    radius: float = Query(1.5),
    zone_id: str | None = Query(None),
):
    index = get_screen_index()
    return index.query_near(x, y, radius, zone_id)


@app.get(
    "/layout/postgis/near",
    response_model=list[Screen],
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def query_screens_near_postgis(
    lat: float = Query(..., description="Latitude (WGS-84)", ge=-90, le=90),
    lon: float = Query(..., description="Longitude (WGS-84)", ge=-180, le=180),
    radius_m: float = Query(30.0, description="Search radius in metres", ge=0.1, le=10000),
    zone_id: str | None = Query(None),
):
    """
    PostGIS ST_DWithin spatial query.
    Επιστρέφει screens εντός radius_m μέτρων από το σημείο (lat, lon).
    Χρησιμοποιεί GIST index στη DB — συγκρίσιμο με /layout/query/near (R-Tree in-memory).
    """
    index = get_screen_index()
    return index.query_near_postgis(lat=lat, lon=lon, radius_m=radius_m, zone_id=zone_id)


@app.get(
    "/layout/distributed/near",
    response_model=list[DistributedResult],
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def query_screens_distributed_near(
    x: float = Query(...),
    y: float = Query(...),
    radius: float = Query(5.0),
    zone_id: str | None = Query(None),
):
    """
    Distributed Index fan-out query (MapReduce simulation).
    """
    dist_index = get_distributed_index()
    raw = dist_index.query_near(x=x, y=y, radius=radius, zone_id=zone_id)
    return [DistributedResult(**r) for r in raw]


@app.get(
    "/layout/multiindex",
    response_model=list[MultiIndexKey],
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def get_multiindex_keys(
    ad_category: str | None = Query(None),
    time_window: str | None = Query(None),
):
    index = get_screen_index()
    return index.build_keys(ad_category=ad_category, time_window=time_window)


@app.get(
    "/layout/recommendation/screen",
    response_model=ScreenRecommendation,
    dependencies=[Depends(require_scope(["recommendation:read"]))],
)
def recommend_screen_endpoint(
    x: float = Query(...),
    y: float = Query(...),
    radius: float = Query(10.0),
    zone_id: str | None = Query(None),
    screen_type: str | None = Query(None),
    ad_category: str | None = Query(None),
    time_window: str | None = Query(None),
):
    index = get_screen_index()
    result = index.recommend_screen(
        x=x, y=y, radius=radius, zone_id=zone_id,
        screen_type=screen_type, ad_category=ad_category, time_window=time_window,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="No suitable screen found")
    key, distance = result
    return ScreenRecommendation(
        screen_id=key.screen_id, zone_id=key.zone_id,
        x=key.x, y=key.y, screen_type=key.screen_type,
        ad_category=key.ad_category, time_window=key.time_window, distance=distance,
    )


@app.get(
    "/recommendation/advertisements/{ad_id}/screen",
    response_model=ScreenRecommendation,
    dependencies=[Depends(require_scope(["recommendation:read"]))],
)
def recommend_screen_for_ad(
    ad_id: int,
    x: float = Query(...),
    y: float = Query(...),
    radius: float = Query(10.0),
    screen_type: str | None = Query(None),
    ad_category: str | None = Query(None),
    time_window: str | None = Query(None),
):
    ad = AdvertisementService.get_by_id(ad_id)
    if ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    index = get_screen_index()
    result = index.recommend_screen(
        x=x, y=y, radius=radius, zone_id=ad.zone,
        screen_type=screen_type, ad_category=ad_category, time_window=time_window,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="No suitable screen found")
    key, distance = result
    return ScreenRecommendation(
        screen_id=key.screen_id, zone_id=key.zone_id,
        x=key.x, y=key.y, screen_type=key.screen_type,
        ad_category=key.ad_category, time_window=key.time_window, distance=distance,
    )


# ── BENCHMARK ──────────────────────────────────────────
@app.get(
    "/benchmark/spatial",
    dependencies=[Depends(require_scope(["layout:read"]))],
)
def benchmark_spatial(
    x: float = Query(2.0, description="Grid X (col) for R-Tree / Distributed"),
    y: float = Query(2.0, description="Grid Y (row) for R-Tree / Distributed"),
    radius: float = Query(10.0, description="Search radius in grid units"),
    lat: float = Query(38.2467, description="Latitude (WGS-84) for PostGIS", ge=-90, le=90),
    lon: float = Query(21.7346, description="Longitude (WGS-84) for PostGIS", ge=-180, le=180),
    radius_m: float = Query(50.0, description="Search radius in metres for PostGIS", ge=0.1, le=10000),
    repeats: int = Query(20, ge=1, le=100, description="Query repetitions per method"),
):
    """
    Live spatial benchmark: R-Tree vs PostGIS vs Distributed.
    """
    index = get_screen_index()
    dist_index = get_distributed_index()

    def bench(fn):
        t0 = time.perf_counter()
        for _ in range(repeats):
            fn()
        return round((time.perf_counter() - t0) / repeats * 1000, 4)

    t_rtree   = bench(lambda: index.query_near(x, y, radius))
    t_kdtree  = bench(lambda: index.query_near_kdtree(x, y, radius))
    t_grid    = bench(lambda: index.query_near_grid(x, y, radius))
    t_dist    = bench(lambda: dist_index.query_near(x, y, radius))

    postgis_error = None
    try:
        t_postgis = bench(lambda: index.query_near_postgis(lat, lon, radius_m))
    except Exception as e:
        t_postgis = None
        postgis_error = str(e)

    rtree_count   = len(index.query_near(x, y, radius))
    kdtree_count  = len(index.query_near_kdtree(x, y, radius))
    grid_count    = len(index.query_near_grid(x, y, radius))
    dist_count    = len(dist_index.query_near(x, y, radius))
    postgis_count = 0
    if postgis_error is None:
        try:
            postgis_count = len(index.query_near_postgis(lat, lon, radius_m))
        except Exception:
            pass

    return {
        "params": {
            "x": x, "y": y, "radius": radius,
            "lat": lat, "lon": lon, "radius_m": radius_m,
            "repeats": repeats,
        },
        "results": {
            "rtree_ms":       t_rtree,
            "kdtree_ms":      t_kdtree,
            "grid_ms":        t_grid,
            "distributed_ms": t_dist,
            "postgis_ms":     t_postgis,
        },
        "counts": {
            "rtree":       rtree_count,
            "kdtree":      kdtree_count,
            "grid":        grid_count,
            "distributed": dist_count,
            "postgis":     postgis_count,
        },
        "postgis_error": postgis_error,
    }


# ── PLACEMENTS ─────────────────────────────────────────
@app.get(
    "/placements",
    response_model=list[AdPlacement],
    dependencies=[Depends(require_scope(["placements:read"]))],
)
def list_placements():
    return PlacementService.list_all()


@app.get(
    "/placements/screen/{screen_id}",
    response_model=list[AdPlacement],
    dependencies=[Depends(require_scope(["placements:read"]))],
)
def list_placements_by_screen(screen_id: str):
    return PlacementService.list_by_screen(screen_id)


@app.post(
    "/placements/recommend_and_assign/advertisements/{ad_id}",
    response_model=AdPlacement,
    dependencies=[Depends(require_scope(["placements:write"]))],
)
async def recommend_and_assign_ad_for_screen(
    ad_id: int,
    x: float = Query(...),
    y: float = Query(...),
    radius: float = Query(10.0),
    screen_type: str | None = Query(None),
    ad_category: str | None = Query(None),
    time_window: str | None = Query(None),
):
    ad = AdvertisementService.get_by_id(ad_id)
    if ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    index = get_screen_index()
    result = index.recommend_screen(
        x=x, y=y, radius=radius, zone_id=ad.zone,
        screen_type=screen_type, ad_category=ad_category, time_window=time_window,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="No suitable screen found")
    key, _distance = result
    placement = PlacementService.assign_ad(ad_id=ad.id, key=key)
    await ws_manager.broadcast_placement_assigned(placement)
    return placement


# ── SECURITY / THREAT DETECTION API ───────────────────────────────────────
@app.get(
    "/security/alerts",
    dependencies=[Depends(require_scope(["security:read"]))],
)
def get_security_alerts():
    """Active security alerts."""
    from app.security.threat_engine import get_threat_engine
    engine = get_threat_engine()
    return engine.get_alerts()


@app.get(
    "/security/events",
    dependencies=[Depends(require_scope(["security:read"]))],
)
def get_security_events(
    event_type: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Recent security events, optionally filtered by type."""
    from app.security.threat_engine import get_threat_engine
    engine = get_threat_engine()
    return engine.get_events(event_type=event_type, limit=limit)


@app.get(
    "/security/stats",
    dependencies=[Depends(require_scope(["security:read"]))],
)
def get_security_stats():
    """Aggregate statistics per event type."""
    from app.security.threat_engine import get_threat_engine
    engine = get_threat_engine()
    return engine.get_stats()


@app.get(
    "/security/comparison",
    dependencies=[Depends(require_scope(["security:read"]))],
)
def get_security_comparison():
    """Rule-based vs Statistical detector comparison data."""
    from app.security.threat_engine import get_threat_engine
    engine = get_threat_engine()
    return engine.get_comparison()
