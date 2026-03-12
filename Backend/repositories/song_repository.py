from __future__ import annotations
from mysql.connector import IntegrityError
from models.db import DBContext


class SongRepository:

    # ── Lectura ─────────────────────────────────────────────────────────

    def get_all(self) -> list[dict]:
        """
        Lista todas las canciones que tienen datos MP3.
        No carga el blob para evitar tráfico innecesario.
        """
        query = (
            "SELECT id, title, artist "
            "FROM songs "
            "WHERE mp3_data IS NOT NULL AND LENGTH(mp3_data) > 0"
        )
        with DBContext() as (_, cur):
            cur.execute(query)
            rows = cur.fetchall()

        return [{"id": r[0], "title": r[1], "artist": r[2]} for r in rows]

    def get_by_id(self, song_id: int) -> dict | None:
        """Devuelve {id, title, artist, mp3_data} o None."""
        query = (
            "SELECT id, title, artist, mp3_data "
            "FROM songs WHERE id = %s"
        )
        with DBContext() as (_, cur):
            cur.execute(query, (song_id,))
            row = cur.fetchone()

        if not row:
            return None

        return {
            "id":       row[0],
            "title":    row[1],
            "artist":   row[2],
            "mp3_data": bytes(row[3]) if row[3] is not None else b"",
        }

    # ── Escritura ────────────────────────────────────────────────────────

    def insert(self, title: str, artist: str, mp3_data: bytes) -> int:
        """
        Inserta una canción nueva y devuelve su id.
        Lanza IntegrityError si ya existe (title, artist) — el service la captura.
        """
        query = (
            "INSERT INTO songs (title, artist, mp3_data, created_at) "
            "VALUES (%s, %s, %s, NOW())"
        )
        with DBContext() as (_, cur):
            cur.execute(query, (title, artist, mp3_data))
            return cur.lastrowid