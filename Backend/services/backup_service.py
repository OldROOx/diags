from __future__ import annotations

from repositories.song_repository   import SongRepository
from repositories.backup_repository import BackupRepository
from exceptions import SongNotFoundError, BackupNotFoundError, EmptyAudioError


class BackupService:

    def __init__(
        self,
        song_repo:   SongRepository   | None = None,
        backup_repo: BackupRepository | None = None,
    ):
        self._songs   = song_repo   or SongRepository()
        self._backups = backup_repo or BackupRepository()

    # ── Casos de uso ─────────────────────────────────────────────────────

    def list_backups(self) -> list[dict]:
        """Devuelve todos los backups ordenados por fecha."""
        return self._backups.get_all()

    def backup_song(self, song_id: int, note: str, backed_by: str) -> int:
        """
        Crea un backup de una canción existente.
        Devuelve el backup_id generado.
        Lanza SongNotFoundError si la canción no existe.
        """
        song = self._songs.get_by_id(song_id)
        if song is None:
            raise SongNotFoundError(song_id)

        return self._backups.insert(
            original_song_id=song["id"],
            title=song["title"],
            artist=song["artist"],
            mp3_data=song["mp3_data"],
            note=note,
            backed_by=backed_by,
        )

    def get_audio(self, backup_id: int) -> dict:
        """
        Devuelve {title, mp3_data} del backup para hacer streaming.
        Lanza BackupNotFoundError o EmptyAudioError si no puede servir audio.
        """
        backup = self._backups.get_by_id(backup_id)
        if backup is None:
            raise BackupNotFoundError(backup_id)
        if not backup["mp3_data"]:
            raise EmptyAudioError(f"backup id={backup_id}")
        return backup

    def store_uploaded_backup(
        self,
        title:    str,
        artist:   str,
        mp3_data: bytes,
    ) -> int:
        """
        Guarda un backup subido directamente (sin canción original en BD).
        Usado por upload_to_db.py.
        """
        return self._backups.insert(
            original_song_id=None,
            title=title,
            artist=artist,
            mp3_data=mp3_data,
            note="uploaded backup file",
            backed_by="upload_to_db",
        )