import os
import base64
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from services.song_service   import SongService
from services.backup_service import BackupService
from exceptions import DuplicateSongError

UPLOAD_DIR     = Config.UPLOAD_DIR
SUPPORTED_EXTS = {".mp3", ".b64"}

_song_svc   = SongService()
_backup_svc = BackupService()


def _read_as_bytes(path: str) -> bytes:
    """Lee el archivo y lo decodifica desde base64 si es texto codificado."""
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        return base64.b64decode(raw, validate=True)
    except Exception:
        return raw


def _stem(filename: str) -> str:
    name, _ = os.path.splitext(filename)
    return name.strip()


def process_file(filename: str) -> None:
    _, ext = os.path.splitext(filename)
    if ext.lower() not in SUPPORTED_EXTS:
        print(f"  [SKIP]   Extensión no soportada: {filename}")
        return

    path = os.path.join(UPLOAD_DIR, filename)
    try:
        data  = _read_as_bytes(path)
        title = _stem(filename)

        if "backup" in filename.lower():
            bid = _backup_svc.store_uploaded_backup(
                title=title,
                artist="uploader",
                mp3_data=data,
            )
            print(f"  [BACKUP] '{title}' → songs_backup (id={bid})")
        else:
            sid = _song_svc.add_song(
                title=title,
                artist="Nuevas Subidas",
                mp3_data=data,
            )
            print(f"  [SONG]   '{title}' → songs (id={sid})")

    except DuplicateSongError as e:
        print(f"  [SKIP]   Duplicado: {e}")
    except Exception as e:
        print(f"  [ERROR]  {filename}: {e}")


def main() -> None:
    if not os.path.isdir(UPLOAD_DIR):
        print(f"La carpeta '{UPLOAD_DIR}' no existe. Créala y coloca archivos .mp3 o .b64.")
        return

    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    if not files:
        print(f"No se encontraron archivos en '{UPLOAD_DIR}'.")
        return

    print(f"Procesando {len(files)} archivo(s) en '{UPLOAD_DIR}'...\n")
    for f in sorted(files):
        process_file(f)
    print("\nProceso finalizado.")


if __name__ == "__main__":
    main()