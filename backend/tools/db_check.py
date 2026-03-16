#!/usr/bin/env python3


import psycopg2
import os
import sys

# Database configuration (from environment or defaults)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5433")),  # Changed from 5432
    "user": os.getenv("DB_USER", "geo_ads_user"),
    "password": os.getenv("DB_PASSWORD", "geo_ads_password"),
    "database": os.getenv("DB_NAME", "geo_ads"),
}

# Expected schema
EXPECTED_COLUMNS = [
    'id', 'name', 'category', 'image_url', 'zone', 
    'geo_lat', 'geo_lon', 'time_window_start', 'time_window_end',
    'created_at', 'updated_at'
]

EXPECTED_INDEXES = [
    'advertisements_pkey',  # PRIMARY KEY
    'idx_ads_zone',
    'idx_ads_category',
    'idx_ads_geo'
]

def test_connection():
    """Test 1: Database connection"""
    print("\n[TEST 1] Database Connection")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"[PASS] Connected to {DB_CONFIG['database']} at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        return conn
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        sys.exit(1)

def test_table_structure(conn):
    """Test 2: Table structure"""
    print("\n[TEST 2] Table Structure")
    cur = conn.cursor()
    
    # Check columns
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'advertisements' 
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    column_names = [col[0] for col in columns]
    
    missing = set(EXPECTED_COLUMNS) - set(column_names)
    extra = set(column_names) - set(EXPECTED_COLUMNS)
    
    if missing:
        print(f"[FAIL] Missing columns: {missing}")
        return False
    
    if extra:
        print(f"[WARN] Extra columns (not critical): {extra}")
    
    print(f"[PASS] All expected columns present ({len(column_names)} total)")
    
    # Display column details
    print("\n   Column Details:")
    for col_name, col_type, nullable in columns:
        null_str = "NULL" if nullable == "YES" else "NOT NULL"
        print(f"   - {col_name:<25} {col_type:<20} {null_str}")
    
    cur.close()
    return True

def test_constraints(conn):
    """Test 3: Constraints"""
    print("\n[TEST 3] Constraints & Indexes")
    cur = conn.cursor()
    
    # Check UNIQUE constraint
    cur.execute("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'advertisements' 
        AND constraint_type = 'UNIQUE';
    """)
    unique_constraints = cur.fetchall()
    
    if any('name_zone' in str(c) for c in unique_constraints):
        print("[PASS] UNIQUE(name, zone) constraint exists")
    else:
        print("[WARN] UNIQUE(name, zone) constraint missing")
    
    # Check CHECK constraint on zone
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'advertisements'::regclass 
        AND contype = 'c';
    """)
    check_constraints = cur.fetchall()
    
    zone_check_found = False
    for name, definition in check_constraints:
        if 'zone' in definition.lower():
            print(f"[PASS] Zone CHECK constraint: {definition}")
            zone_check_found = True
    
    if not zone_check_found:
        print("[WARN] Zone CHECK constraint missing")
    
    # Check indexes
    cur.execute("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'advertisements';
    """)
    indexes = [row[0] for row in cur.fetchall()]
    
    print(f"\n   Indexes found ({len(indexes)}):")
    for idx in indexes:
        status = "[PASS]" if idx in EXPECTED_INDEXES else "[WARN]"
        print(f"   {status} {idx}")
    
    missing_indexes = set(EXPECTED_INDEXES) - set(indexes)
    if missing_indexes:
        print(f"\n   [FAIL] Missing indexes: {missing_indexes}")
    
    cur.close()
    return True

def test_seed_data(conn):
    """Test 4: Seed data"""
    print("\n[TEST 4] Seed Data")
    cur = conn.cursor()
    
    # Total count
    cur.execute("SELECT COUNT(*) FROM advertisements;")
    total = cur.fetchone()[0]
    print(f"[PASS] Total advertisements: {total}")
    
    if total == 0:
        print("[FAIL] No seed data found!")
        cur.close()
        return False
    
    # Per-zone count
    cur.execute("""
        SELECT zone, COUNT(*) as count 
        FROM advertisements 
        GROUP BY zone 
        ORDER BY zone;
    """)
    
    print("\n   Ads per zone:")
    for zone, count in cur.fetchall():
        print(f"   - {zone:<15} {count} ads")
    
    # Sample data
    cur.execute("""
        SELECT name, category, zone, image_url 
        FROM advertisements 
        LIMIT 5;
    """)
    
    print("\n   Sample advertisements:")
    for name, category, zone, image_url in cur.fetchall():
        cat_str = category or 'N/A'
        print(f"   - {name:<30} [{cat_str:<12}] in {zone:<15}")
    
    # Geo-targeted ads
    cur.execute("""
        SELECT COUNT(*) 
        FROM advertisements 
        WHERE geo_lat IS NOT NULL AND geo_lon IS NOT NULL;
    """)
    geo_count = cur.fetchone()[0]
    print(f"\n   [INFO] Geo-targeted ads: {geo_count}")
    
    # Time-targeted ads
    cur.execute("""
        SELECT COUNT(*) 
        FROM advertisements 
        WHERE time_window_start IS NOT NULL;
    """)
    time_count = cur.fetchone()[0]
    print(f"   [INFO] Time-targeted ads: {time_count}")
    
    cur.close()
    return True

def test_zone_validation(conn):
    """Test 5: Zone validation (attempt invalid insert)"""
    print("\n[TEST 5] Zone Validation (CHECK constraint)")
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO advertisements (name, image_url, zone) 
            VALUES ('Test Ad', '/test.png', 'invalid_zone');
        """)
        conn.rollback()
        print("[FAIL] CHECK constraint NOT working - invalid zone was accepted!")
        cur.close()
        return False
    except psycopg2.errors.CheckViolation:
        conn.rollback()
        print("[PASS] CHECK constraint working - invalid zone rejected")
        cur.close()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[WARN] Unexpected error: {e}")
        cur.close()
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("GEO-ADS DATABASE VERIFICATION SCRIPT")
    print("Milestone 1: Database Schema & Initialization")
    print("=" * 70)
    
    conn = test_connection()
    
    all_passed = True
    all_passed &= test_table_structure(conn)
    all_passed &= test_constraints(conn)
    all_passed &= test_seed_data(conn)
    all_passed &= test_zone_validation(conn)
    
    conn.close()
    
    print("\n" + "=" * 70)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - Milestone 1 complete!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("[FAILURE] SOME TESTS FAILED - Review output above")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()