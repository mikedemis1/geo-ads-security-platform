-- ============================================================================
-- GEO-ADS Advertisement Schema
-- Milestone 1: Database Schema & Initialization
-- Phase 2: PostGIS spatial extension + screens table
-- ============================================================================

-- PostGIS spatial extension (requires postgis/postgis Docker image)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Drop tables if exist (only for development)
DROP TABLE IF EXISTS screens CASCADE;
DROP TABLE IF EXISTS advertisements CASCADE;

CREATE TABLE advertisements (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- Basic ad info
    name TEXT NOT NULL,
    category TEXT,  -- 'sports', 'beverage', 'automotive', 'tech', etc.
    image_url TEXT NOT NULL,
    
    -- Zone assignment with validation
    zone TEXT NOT NULL CHECK (zone IN ('glassfloor', 'surrounding', 'megatron')),
    
    -- Targeting metadata (for future geo/time-based recommendations)
    geo_lat DECIMAL(9,6),  -- Latitude (nullable for non-geo targeted ads)
    geo_lon DECIMAL(9,6),  -- Longitude (nullable for non-geo targeted ads)
    time_window_start TIME,  -- Start time for time-based targeting
    time_window_end TIME,    -- End time for time-based targeting
    
    -- Audit timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Business constraints
    CONSTRAINT advertisements_name_zone_uniq UNIQUE (name, zone)
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

CREATE INDEX idx_ads_zone ON advertisements(zone);
CREATE INDEX idx_ads_category ON advertisements(category);
CREATE INDEX idx_ads_geo ON advertisements(geo_lat, geo_lon) WHERE geo_lat IS NOT NULL;

-- ============================================================================
-- Seed Data (idempotent - safe for repeated runs)
-- ============================================================================

INSERT INTO advertisements (name, category, image_url, zone, geo_lat, geo_lon, time_window_start, time_window_end) VALUES
    -- GlassFloor ads
    ('Nike Air Max', 'sports', '/static/ads/airmax.png', 'glassfloor', 38.246639, 21.734573, '14:00:00', '22:00:00'),
    ('Under Armour Basketball', 'sports', '/static/ads/underarmour.png', 'glassfloor', NULL, NULL, NULL, NULL),
    
    -- Surrounding Screen ads
    ('Adidas Predator', 'sports', '/static/ads/predator.png', 'surrounding', NULL, NULL, '18:00:00', '23:00:00'),
    ('Puma Running', 'sports', '/static/ads/puma.png', 'surrounding', NULL, NULL, NULL, NULL),
    
    -- Megatron ads
    ('Coca Cola', 'beverage', '/static/ads/cocacola.png', 'megatron', NULL, NULL, '12:00:00', '23:59:59'),
    ('Pepsi Max', 'beverage', '/static/ads/pepsi.png', 'megatron', NULL, NULL, NULL, NULL),
    ('BMW M Series', 'automotive', '/static/ads/bmw.png', 'megatron', 38.246639, 21.734573, NULL, NULL)
    
ON CONFLICT (name, zone) DO NOTHING;

-- ============================================================================
-- Screens Table (Phase 2: PostGIS spatial)
-- Each screen gets a real GEOGRAPHY(Point,4326) location.
-- Venue center: 38.246639, 21.734573 (Patras area)
-- Grid spacing: ~5m (lat_step=0.000045, lon_step=0.000057)
-- ============================================================================

CREATE TABLE screens (
    id          TEXT PRIMARY KEY,
    zone_id     TEXT NOT NULL,
    row_idx     INT  NOT NULL,
    col_idx     INT  NOT NULL,
    screen_type TEXT NOT NULL,
    location    GEOGRAPHY(Point, 4326) NOT NULL
);

-- GIST spatial index enables O(log n) ST_DWithin queries
CREATE INDEX idx_screens_location ON screens USING GIST(location);
CREATE INDEX idx_screens_zone     ON screens(zone_id);

-- ─── GlassFloor 4×4 (16 screens) ────────────────────────────────────────────
-- lat_base=38.2465715, lon_base=21.7344875, step: lat+0.000045 / lon+0.000057
INSERT INTO screens (id, zone_id, row_idx, col_idx, screen_type, location) VALUES
    ('GF-0-0','glassfloor',0,0,'glassfloor_tile', ST_MakePoint(21.7344875,38.2465715)::geography),
    ('GF-0-1','glassfloor',0,1,'glassfloor_tile', ST_MakePoint(21.7345445,38.2465715)::geography),
    ('GF-0-2','glassfloor',0,2,'glassfloor_tile', ST_MakePoint(21.7346015,38.2465715)::geography),
    ('GF-0-3','glassfloor',0,3,'glassfloor_tile', ST_MakePoint(21.7346585,38.2465715)::geography),
    ('GF-1-0','glassfloor',1,0,'glassfloor_tile', ST_MakePoint(21.7344875,38.2466165)::geography),
    ('GF-1-1','glassfloor',1,1,'glassfloor_tile', ST_MakePoint(21.7345445,38.2466165)::geography),
    ('GF-1-2','glassfloor',1,2,'glassfloor_tile', ST_MakePoint(21.7346015,38.2466165)::geography),
    ('GF-1-3','glassfloor',1,3,'glassfloor_tile', ST_MakePoint(21.7346585,38.2466165)::geography),
    ('GF-2-0','glassfloor',2,0,'glassfloor_tile', ST_MakePoint(21.7344875,38.2466615)::geography),
    ('GF-2-1','glassfloor',2,1,'glassfloor_tile', ST_MakePoint(21.7345445,38.2466615)::geography),
    ('GF-2-2','glassfloor',2,2,'glassfloor_tile', ST_MakePoint(21.7346015,38.2466615)::geography),
    ('GF-2-3','glassfloor',2,3,'glassfloor_tile', ST_MakePoint(21.7346585,38.2466615)::geography),
    ('GF-3-0','glassfloor',3,0,'glassfloor_tile', ST_MakePoint(21.7344875,38.2467065)::geography),
    ('GF-3-1','glassfloor',3,1,'glassfloor_tile', ST_MakePoint(21.7345445,38.2467065)::geography),
    ('GF-3-2','glassfloor',3,2,'glassfloor_tile', ST_MakePoint(21.7346015,38.2467065)::geography),
    ('GF-3-3','glassfloor',3,3,'glassfloor_tile', ST_MakePoint(21.7346585,38.2467065)::geography);

-- ─── Surrounding 2×4 (8 screens) ────────────────────────────────────────────
-- Offset: +3 rows north of GlassFloor center
-- lat_base=38.2467740, lon_base=21.7344875
INSERT INTO screens (id, zone_id, row_idx, col_idx, screen_type, location) VALUES
    ('SUR-0-0','surrounding',0,0,'surrounding_banner', ST_MakePoint(21.7344875,38.2467740)::geography),
    ('SUR-0-1','surrounding',0,1,'surrounding_banner', ST_MakePoint(21.7345445,38.2467740)::geography),
    ('SUR-0-2','surrounding',0,2,'surrounding_banner', ST_MakePoint(21.7346015,38.2467740)::geography),
    ('SUR-0-3','surrounding',0,3,'surrounding_banner', ST_MakePoint(21.7346585,38.2467740)::geography),
    ('SUR-1-0','surrounding',1,0,'surrounding_banner', ST_MakePoint(21.7344875,38.2468190)::geography),
    ('SUR-1-1','surrounding',1,1,'surrounding_banner', ST_MakePoint(21.7345445,38.2468190)::geography),
    ('SUR-1-2','surrounding',1,2,'surrounding_banner', ST_MakePoint(21.7346015,38.2468190)::geography),
    ('SUR-1-3','surrounding',1,3,'surrounding_banner', ST_MakePoint(21.7346585,38.2468190)::geography);

-- ─── Megatron 2×2 (4 screens) ────────────────────────────────────────────────
-- Large screens, offset: +6 rows north, centered
-- lat_base=38.2469090, lon_base=21.7345445
INSERT INTO screens (id, zone_id, row_idx, col_idx, screen_type, location) VALUES
    ('MEGA-0-0','megatron',0,0,'megatron_panel', ST_MakePoint(21.7345445,38.2469090)::geography),
    ('MEGA-0-1','megatron',0,1,'megatron_panel', ST_MakePoint(21.7346015,38.2469090)::geography),
    ('MEGA-1-0','megatron',1,0,'megatron_panel', ST_MakePoint(21.7345445,38.2469540)::geography),
    ('MEGA-1-1','megatron',1,1,'megatron_panel', ST_MakePoint(21.7346015,38.2469540)::geography);

-- ============================================================================
-- Verification Queries (for manual testing)
-- ============================================================================

-- Uncomment to verify after initialization:
-- SELECT COUNT(*) as total_ads FROM advertisements;
-- SELECT zone, COUNT(*) as ads_per_zone FROM advertisements GROUP BY zone;
-- SELECT COUNT(*) as total_screens FROM screens;
-- SELECT PostGIS_version();
-- SELECT id, zone_id, ST_AsText(location) FROM screens LIMIT 5;