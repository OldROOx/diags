from __future__ import annotations
from mysql.connector import IntegrityError

from repositories.song_repository import SongRepository
from exceptions import SongNotFoundError, EmptyAudioError, DuplicateSongError


class SongService:

    def __init__(self, song_repo: SongRepository | None = None):
        self._songs = song_repo or SongRepository()

    # ── Casos de uso ─────────────────────────────────────────────────────

    def list_songs(self) -> list[dict]:
        """Devuelve todas las canciones con audio disponible."""
        return self._songs.get_all()

    def get_audio(self, song_id: int) -> dict:
        """
        Devuelve {title, mp3_data} listo para hacer streaming.
        Lanza SongNotFoundError o EmptyAudioError si no puede servir audio.
        """
        song = self._songs.get_by_id(song_id)
        if song is None:
            raise SongNotFoundError(song_id)
        if not song["mp3_data"]:
            raise EmptyAudioError(f"canción id={song_id}")
        return song

    def add_song(self, title: str, artist: str, mp3_data: bytes) -> int:
        """
        Registra una canción nueva y devuelve su id.
        Lanza DuplicateSongError si (title, artist) ya existe.
        """
        title  = title.strip()
        artist = artist.strip()
        try:
            return self._songs.insert(title, artist, mp3_data)
        except IntegrityError:
            raise DuplicateSongError(title, artist)