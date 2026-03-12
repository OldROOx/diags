"""
test_backup_service.py – Tests T24 a T36
Pruebas unitarias para services/backup_service.py.

Se inyectan mocks de SongRepository y BackupRepository para aislar
la lógica de negocio de BackupService sin acceso a base de datos.
"""

import pytest
from unittest.mock import MagicMock

from services.backup_service import BackupService
from exceptions import SongNotFoundError, BackupNotFoundError, EmptyAudioError


# ─────────────────────────────────────────────────────────────────────────────
# T24 – list_backups() devuelve lista vacía cuando no hay backups
# ─────────────────────────────────────────────────────────────────────────────
def test_T24_list_backups_devuelve_lista_vacia():
    """
    T24: Cuando el backup_repo no tiene registros (get_all retorna []),
    BackupService.list_backups() debe devolver [] sin lanzar excepciones.
    """
    mock_song_repo = MagicMock()
    mock_backup_repo = MagicMock()
    mock_backup_repo.get_all.return_value = []
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    result = service.list_backups()

    assert result == []


# ─────────────────────────────────────────────────────────────────────────────
# T25 – list_backups() devuelve exactamente los datos del backup_repo
# ─────────────────────────────────────────────────────────────────────────────
def test_T25_list_backups_devuelve_datos_del_repo():
    """
    T25: list_backups() debe retornar sin modificar la lista que devuelve
    backup_repo.get_all(), preservando todos los campos del backup
    (id, original_song_id, title, artist, backup_note, backed_up_by, backed_up_at).
    """
    backups = [
        {"id": 1, "original_song_id": 5, "title": "Song", "artist": "Art",
         "backup_note": "test", "backed_up_by": "admin", "backed_up_at": "2024-01-01"}
    ]
    mock_song_repo = MagicMock()
    mock_backup_repo = MagicMock()
    mock_backup_repo.get_all.return_value = backups
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    result = service.list_backups()

    assert result == backups


# ─────────────────────────────────────────────────────────────────────────────
# T26 – backup_song() lanza SongNotFoundError cuando la canción no existe
# ─────────────────────────────────────────────────────────────────────────────
def test_T26_backup_song_lanza_song_not_found_cuando_no_existe():
    """
    T26: backup_song(song_id) primero busca la canción original. Si
    song_repo.get_by_id() devuelve None, debe lanzar SongNotFoundError
    antes de intentar insertar cualquier backup.
    """
    mock_song_repo = MagicMock()
    mock_song_repo.get_by_id.return_value = None
    mock_backup_repo = MagicMock()
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    with pytest.raises(SongNotFoundError):
        service.backup_song(404, note="test", backed_by="tester")


# ─────────────────────────────────────────────────────────────────────────────
# T27 – backup_song() devuelve el backup_id generado
# ─────────────────────────────────────────────────────────────────────────────
def test_T27_backup_song_devuelve_backup_id():
    """
    T27: Cuando la canción existe, backup_song() debe devolver el entero
    que retorna backup_repo.insert() (el lastrowid del nuevo backup).
    """
    song = {"id": 1, "title": "Song", "artist": "Artist", "mp3_data": b"audio"}
    mock_song_repo = MagicMock()
    mock_song_repo.get_by_id.return_value = song
    mock_backup_repo = MagicMock()
    mock_backup_repo.insert.return_value = 77
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    result = service.backup_song(1, note="nota", backed_by="user")

    assert result == 77


# ─────────────────────────────────────────────────────────────────────────────
# T28 – backup_song() pasa el id de la canción original al repo de backups
# ─────────────────────────────────────────────────────────────────────────────
def test_T28_backup_song_pasa_original_song_id_correcto():
    """
    T28: backup_song() debe llamar a backup_repo.insert() con
    original_song_id igual al id de la canción original, para mantener
    la referencia de auditoría entre el backup y su fuente.
    """
    song = {"id": 10, "title": "X", "artist": "Y", "mp3_data": b"data"}
    mock_song_repo = MagicMock()
    mock_song_repo.get_by_id.return_value = song
    mock_backup_repo = MagicMock()
    mock_backup_repo.insert.return_value = 1
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    service.backup_song(10, note="n", backed_by="u")

    kwargs = mock_backup_repo.insert.call_args[1]
    assert kwargs["original_song_id"] == 10


# ─────────────────────────────────────────────────────────────────────────────
# T29 – backup_song() copia título y artista de la canción original
# ─────────────────────────────────────────────────────────────────────────────
def test_T29_backup_song_copia_titulo_y_artista():
    """
    T29: backup_song() debe copiar exactamente el title y el artist de la
    canción original al backup, garantizando que el backup refleja la metadata
    de la canción en el momento del backup.
    """
    song = {"id": 2, "title": "My Title", "artist": "My Artist", "mp3_data": b"x"}
    mock_song_repo = MagicMock()
    mock_song_repo.get_by_id.return_value = song
    mock_backup_repo = MagicMock()
    mock_backup_repo.insert.return_value = 5
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    service.backup_song(2, note="n", backed_by="u")

    kwargs = mock_backup_repo.insert.call_args[1]
    assert kwargs["title"] == "My Title"
    assert kwargs["artist"] == "My Artist"


# ─────────────────────────────────────────────────────────────────────────────
# T30 – backup_song() copia el mp3_data de la canción original
# ─────────────────────────────────────────────────────────────────────────────
def test_T30_backup_song_copia_mp3_data():
    """
    T30: backup_song() debe copiar los bytes de mp3_data de la canción
    original al backup, para que el backup sea una copia fiel del audio.
    """
    audio = b"real_audio_bytes_here"
    song = {"id": 3, "title": "T", "artist": "A", "mp3_data": audio}
    mock_song_repo = MagicMock()
    mock_song_repo.get_by_id.return_value = song
    mock_backup_repo = MagicMock()
    mock_backup_repo.insert.return_value = 9
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    service.backup_song(3, note="n", backed_by="u")

    kwargs = mock_backup_repo.insert.call_args[1]
    assert kwargs["mp3_data"] == audio


# ─────────────────────────────────────────────────────────────────────────────
# T31 – backup_song() pasa note y backed_by al repo de backups
# ─────────────────────────────────────────────────────────────────────────────
def test_T31_backup_song_pasa_note_y_backed_by():
    """
    T31: Los parámetros de auditoría 'note' y 'backed_by' proporcionados
    a backup_song() deben ser transmitidos sin modificar a backup_repo.insert(),
    para que el registro de quién hizo el backup y por qué sea fiel.
    """
    song = {"id": 4, "title": "T", "artist": "A", "mp3_data": b"d"}
    mock_song_repo = MagicMock()
    mock_song_repo.get_by_id.return_value = song
    mock_backup_repo = MagicMock()
    mock_backup_repo.insert.return_value = 3
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    service.backup_song(4, note="backup semanal", backed_by="admin")

    kwargs = mock_backup_repo.insert.call_args[1]
    assert kwargs["note"] == "backup semanal"
    assert kwargs["backed_by"] == "admin"


# ─────────────────────────────────────────────────────────────────────────────
# T32 – get_audio() devuelve el dict del backup cuando existe y tiene audio
# ─────────────────────────────────────────────────────────────────────────────
def test_T32_get_audio_backup_devuelve_dict_cuando_existe():
    """
    T32: BackupService.get_audio(backup_id) debe retornar el dict completo
    (con mp3_data) cuando el backup existe y tiene datos de audio válidos.
    """
    backup = {"id": 20, "title": "Backup Song", "artist": "Art", "mp3_data": b"backup_audio"}
    mock_song_repo = MagicMock()
    mock_backup_repo = MagicMock()
    mock_backup_repo.get_by_id.return_value = backup
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    result = service.get_audio(20)

    assert result == backup


# ─────────────────────────────────────────────────────────────────────────────
# T33 – get_audio() lanza BackupNotFoundError cuando el backup no existe
# ─────────────────────────────────────────────────────────────────────────────
def test_T33_get_audio_backup_lanza_backup_not_found_cuando_no_existe():
    """
    T33: Si backup_repo.get_by_id() devuelve None, BackupService.get_audio()
    debe lanzar BackupNotFoundError con el backup_id correcto, en lugar de
    un AttributeError al intentar acceder a None["mp3_data"].
    """
    mock_song_repo = MagicMock()
    mock_backup_repo = MagicMock()
    mock_backup_repo.get_by_id.return_value = None
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    with pytest.raises(BackupNotFoundError) as exc_info:
        service.get_audio(888)

    assert exc_info.value.backup_id == 888


# ─────────────────────────────────────────────────────────────────────────────
# T34 – get_audio() lanza EmptyAudioError cuando mp3_data del backup es vacío
# ─────────────────────────────────────────────────────────────────────────────
def test_T34_get_audio_backup_lanza_empty_audio_cuando_vacio():
    """
    T34: Si el backup existe pero su mp3_data es b"" (bytes vacíos),
    BackupService.get_audio() debe lanzar EmptyAudioError en lugar de
    devolver una respuesta de audio vacía.
    """
    backup = {"id": 15, "title": "Empty Backup", "artist": "Ghost", "mp3_data": b""}
    mock_song_repo = MagicMock()
    mock_backup_repo = MagicMock()
    mock_backup_repo.get_by_id.return_value = backup
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    with pytest.raises(EmptyAudioError):
        service.get_audio(15)


# ─────────────────────────────────────────────────────────────────────────────
# T35 – store_uploaded_backup() devuelve el backup_id generado
# ─────────────────────────────────────────────────────────────────────────────
def test_T35_store_uploaded_backup_devuelve_id():
    """
    T35: store_uploaded_backup() debe devolver el entero que retorna
    backup_repo.insert(), correspondiente al id del backup creado.
    Este método se usa desde upload_to_db.py para importar archivos externos.
    """
    mock_song_repo = MagicMock()
    mock_backup_repo = MagicMock()
    mock_backup_repo.insert.return_value = 55
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    result = service.store_uploaded_backup("Title", "Artist", b"data")

    assert result == 55


# ─────────────────────────────────────────────────────────────────────────────
# T36 – store_uploaded_backup() llama a insert() con original_song_id=None
# ─────────────────────────────────────────────────────────────────────────────
def test_T36_store_uploaded_backup_usa_original_song_id_none():
    """
    T36: store_uploaded_backup() corresponde a backups sin canción original en BD.
    Debe llamar a backup_repo.insert() con original_song_id=None para representar
    que el backup no tiene referencia a una canción de la tabla songs.
    """
    mock_song_repo = MagicMock()
    mock_backup_repo = MagicMock()
    mock_backup_repo.insert.return_value = 1
    service = BackupService(song_repo=mock_song_repo, backup_repo=mock_backup_repo)

    service.store_uploaded_backup("My Upload", "Uploader", b"bytes")

    kwargs = mock_backup_repo.insert.call_args[1]
    assert kwargs["original_song_id"] is None
