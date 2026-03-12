class BrokenTunesError(Exception):
    """Base para todas las excepciones del dominio."""


class SongNotFoundError(BrokenTunesError):
    def __init__(self, song_id: int):
        self.song_id = song_id
        super().__init__(f"Canción con id={song_id} no encontrada.")


class BackupNotFoundError(BrokenTunesError):
    def __init__(self, backup_id: int):
        self.backup_id = backup_id
        super().__init__(f"Backup con id={backup_id} no encontrado.")


class EmptyAudioError(BrokenTunesError):
    def __init__(self, resource: str):
        super().__init__(f"'{resource}' no tiene datos de audio.")


class DuplicateSongError(BrokenTunesError):
    def __init__(self, title: str, artist: str):
        super().__init__(f"Ya existe una canción con título='{title}' y artista='{artist}'.")