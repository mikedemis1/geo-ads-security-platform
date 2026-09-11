# backend/app/services/advertisement_service.py
from typing import List, Optional
from app.config import get_db_connection
from app.models.advertisement import Advertisement


class AdvertisementService:
    @staticmethod
    def get_all() -> List[Advertisement]:
        """
        Return every row of the advertisements table.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, image_url, zone
            FROM advertisements
            ORDER BY id;
            """
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        ads: List[Advertisement] = []
        for row in rows:
            ads.append(
                Advertisement(
                    id=row[0],
                    name=row[1],
                    image_url=row[2],
                    zone=row[3],
                )
            )
        return ads

    @staticmethod
    def get_by_zone(zone_id: str) -> List[Advertisement]:
        """
        Before: filtered by zone_id (WHERE zone = %s).

        Now: the GEO-ADS UI needs every advertisement
        to be available in every zone
        (GlassFloor, Surrounding, Megatron).

        So zone_id is ignored and all rows are returned.
        The parameter stays for API compatibility.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, image_url, zone
            FROM advertisements
            ORDER BY id;
            """
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        ads: List[Advertisement] = []
        for row in rows:
            ads.append(
                Advertisement(
                    id=row[0],
                    name=row[1],
                    image_url=row[2],
                    zone=row[3],
                )
            )
        return ads

    @staticmethod
    def get_by_id(ad_id: int) -> Optional[Advertisement]:
        """
        Return one advertisement by id.
        Returns None if it does not exist.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, image_url, zone
            FROM advertisements
            WHERE id = %s;
            """,
            (ad_id,),
        )

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row is None:
            return None

        return Advertisement(
            id=row[0],
            name=row[1],
            image_url=row[2],
            zone=row[3],
        )
