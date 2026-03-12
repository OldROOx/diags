from __future__ import annotations
from models.db import DBContext

class BackupRepository:


    def get_all(self) -> list[dict]:
        """Lista todos los backups ordenados por fecha descendente."""
        query = (
            "SELECT id, original_song_id, title, artist, "
            "       backup_note, backed_up_by, backed_up_at "
            "FROM songs_backup "
            "ORDER BY backed_up_at DESC"
        )
        with DBContext() as (_, cur):
            cur.execute(query)
            rows = cur.fetchall()

        return [
            {
                "id":               r[0],
                "original_song_id": r[1],
                "title":            r[2],
                "artist":           r[3],
                "backup_note":      r[4],
                "backed_up_by":     r[5],
                "backed_up_at":     r[6].isoformat() if hasattr(r[6], "isoformat") else r[6],
            }
            for r in rows
        ]

    def get_by_id(self, backup_id: int) -> dict | None:
        """Devuelve {id, title, artist, mp3_data} o None."""
        query = (
            "SELECT id, title, artist, mp3_data "
            "FROM songs_backup WHERE id = %s"
        )
        with DBContext() as (_, cur):
            cur.execute(query, (backup_id,))
            row = cur.fetchone()

        if not row:
            return None

        return {
            "id":       row[0],
            "title":    row[1],
            "artist":   row[2],
            "mp3_data": bytes(row[3]) if row[3] is not None else b"",
        }


    def insert(
        self,
        original_song_id: int | None,
        title: str,
        artist: str,
        mp3_data: bytes,
        note: str,
        backed_by: str,
    ) -> int:
        """
        Inserta un backup y devuelve su id.
        original_song_id puede ser None (backup de archivo externo).
        """
        query = (
            "INSERT INTO songs_backup "
            "  (original_song_id, title, artist, mp3_data, "
            "   backup_note, backed_up_by, backed_up_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, NOW())"
        )
        with DBContext() as (_, cur):
            cur.execute(query, (original_song_id, title, artist, mp3_data, note, backed_by))
            return cur.lastrowid