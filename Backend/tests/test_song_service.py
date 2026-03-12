"""
test_song_service.py – Tests T12 a T23
Pruebas unitarias para services/song_service.py.

Se utiliza inyección de dependencias (mock_repo) para aislar la lógica
de negocio de SongService sin necesitar una base de datos real.
Todos los repositorios son MagicMock configurados por cada test.
"""

import pytest
from unittest.mock import MagicMock, call
from mysql.connector import IntegrityError

from services.song_service import SongService
from exceptions import SongNotFoundError, EmptyAudioError, DuplicateSongError


# ─────────────────────────────────────────────────────────────────────────────
# T12 – list_songs() devuelve lista vacía cuando el repositorio no tiene songs
# ─────────────────────────────────────────────────────────────────────────────
def test_T12_list_songs_devuelve_lista_vacia():
    """
    T12: Cuando el repositorio no tiene canciones (get_all retorna []),
    SongService.list_songs() debe devolver una lista vacía sin lanzar excepciones.
    """
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = []
    service = SongService(song_repo=mock_repo)

    result = service.list_songs()

    assert result == []


# ─────────────────────────────────────────────────────────────────────────────
# T13 – list_songs() devuelve exactamente los datos del repositorio
# ─────────────────────────────────────────────────────────────────────────────
def test_T13_list_songs_devuelve_datos_del_repo():
    """
    T13: list_songs() debe devolver sin modificar la lista que retorna
    el repositorio, preservando todos los campos (id, title, artist).
    """
    canciones = [
        {"id": 1, "title": "Song A", "artist": "Artist X"},
        {"id": 2, "title": "Song B", "artist": "Artist Y"},
    ]
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = canciones
    service = SongService(song_repo=mock_repo)

    result = service.list_songs()

    assert result == canciones


# ─────────────────────────────────────────────────────────────────────────────
# T14 – list_songs() delega al método get_all() del repositorio
# ─────────────────────────────────────────────────────────────────────────────
def test_T14_list_songs_llama_get_all_del_repo():
    """
    T14: list_songs() debe invocar exactamente una vez repo.get_all(),
    sin acceder a otros métodos del repositorio. Verifica que la capa de
    servicio no tiene lógica de acceso a datos propia.
    """
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = []
    service = SongService(song_repo=mock_repo)

    service.list_songs()

    mock_repo.get_all.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# T15 – get_audio() devuelve el dict completo cuando la canción existe y tiene audio
# ─────────────────────────────────────────────────────────────────────────────
def test_T15_get_audio_devuelve_dict_cuando_song_existe():
    """
    T15: get_audio(song_id) debe retornar el dict completo (incluyendo mp3_data)
    cuando el repositorio encuentra la canción y tiene datos de audio válidos.
    """
    song_data = {"id": 5, "title": "Test Song", "artist": "Tester", "mp3_data": b"audio_bytes"}
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = song_data
    service = SongService(song_repo=mock_repo)

    result = service.get_audio(5)

    assert result == song_data


# ─────────────────────────────────────────────────────────────────────────────
# T16 – get_audio() lanza SongNotFoundError cuando el repo devuelve None
# ─────────────────────────────────────────────────────────────────────────────
def test_T16_get_audio_lanza_song_not_found_cuando_no_existe():
    """
    T16: Si el repositorio devuelve None para el song_id solicitado,
    get_audio() debe lanzar SongNotFoundError con el id correcto,
    en lugar de retornar None o lanzar un AttributeError genérico.
    """
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    service = SongService(song_repo=mock_repo)

    with pytest.raises(SongNotFoundError) as exc_info:
        service.get_audio(999)

    assert exc_info.value.song_id == 999


# ─────────────────────────────────────────────────────────────────────────────
# T17 – get_audio() lanza EmptyAudioError cuando mp3_data es bytes vacíos
# ─────────────────────────────────────────────────────────────────────────────
def test_T17_get_audio_lanza_empty_audio_cuando_mp3_data_es_bytes_vacios():
    """
    T17: Cuando la canción existe pero mp3_data = b"" (bytes vacíos),
    get_audio() debe lanzar EmptyAudioError en lugar de devolver una respuesta
    de audio vacía que causaría un reproductor roto en el cliente.
    """
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = {
        "id": 3, "title": "Silent", "artist": "Nobody", "mp3_data": b""
    }
    service = SongService(song_repo=mock_repo)

    with pytest.raises(EmptyAudioError):
        service.get_audio(3)


# ─────────────────────────────────────────────────────────────────────────────
# T18 – get_audio() lanza EmptyAudioError cuando mp3_data es None
# ─────────────────────────────────────────────────────────────────────────────
def test_T18_get_audio_lanza_empty_audio_cuando_mp3_data_es_none():
    """
    T18: Cuando la canción existe pero mp3_data = None,
    get_audio() debe lanzar EmptyAudioError. None es falsy en Python,
    por lo que la condición `if not song["mp3_data"]` la captura correctamente.
    """
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = {
        "id": 7, "title": "No Audio", "artist": "Ghost", "mp3_data": None
    }
    service = SongService(song_repo=mock_repo)

    with pytest.raises(EmptyAudioError):
        service.get_audio(7)


# ─────────────────────────────────────────────────────────────────────────────
# T19 – add_song() devuelve el id generado por el repositorio
# ─────────────────────────────────────────────────────────────────────────────
def test_T19_add_song_devuelve_id_del_repo():
    """
    T19: add_song() debe retornar el entero que devuelve repo.insert(),
    que corresponde al lastrowid (id auto-increment) de la canción nueva.
    """
    mock_repo = MagicMock()
    mock_repo.insert.return_value = 42
    service = SongService(song_repo=mock_repo)

    result = service.add_song("My Song", "My Artist", b"mp3data")

    assert result == 42


# ─────────────────────────────────────────────────────────────────────────────
# T20 – add_song() convierte IntegrityError en DuplicateSongError
# ─────────────────────────────────────────────────────────────────────────────
def test_T20_add_song_lanza_duplicate_cuando_integrity_error():
    """
    T20: Si repo.insert() lanza mysql.connector.IntegrityError (clave única violada),
    add_song() debe capturarla y relanzarla como DuplicateSongError del dominio,
    evitando que detalles de implementación (MySQL) escapen a la capa de rutas.
    """
    mock_repo = MagicMock()
    mock_repo.insert.side_effect = IntegrityError()
    service = SongService(song_repo=mock_repo)

    with pytest.raises(DuplicateSongError):
        service.add_song("Dup Title", "Dup Artist", b"data")


# ─────────────────────────────────────────────────────────────────────────────
# T21 – add_song() elimina espacios del título
# ─────────────────────────────────────────────────────────────────────────────
def test_T21_add_song_strip_titulo():
    """
    T21: add_song() debe aplicar .strip() al título antes de insertarlo,
    para que '  My Song  ' y 'My Song' no generen entradas duplicadas distintas
    en la base de datos.
    """
    mock_repo = MagicMock()
    mock_repo.insert.return_value = 1
    service = SongService(song_repo=mock_repo)

    service.add_song("  My Song  ", "Artist", b"data")

    # Verificar que se llamó con el título sin espacios
    args = mock_repo.insert.call_args[0]
    assert args[0] == "My Song"


# ─────────────────────────────────────────────────────────────────────────────
# T22 – add_song() elimina espacios del artista
# ─────────────────────────────────────────────────────────────────────────────
def test_T22_add_song_strip_artista():
    """
    T22: add_song() debe aplicar .strip() al nombre del artista antes de insertar,
    por la misma razón de normalización que el título (T21).
    """
    mock_repo = MagicMock()
    mock_repo.insert.return_value = 1
    service = SongService(song_repo=mock_repo)

    service.add_song("Song", "  My Artist  ", b"data")

    args = mock_repo.insert.call_args[0]
    assert args[1] == "My Artist"


# ─────────────────────────────────────────────────────────────────────────────
# T23 – add_song() llama a repo.insert() con los argumentos normalizados
# ─────────────────────────────────────────────────────────────────────────────
def test_T23_add_song_llama_insert_con_args_correctos():
    """
    T23: Además de los strips, add_song() debe llamar a repo.insert()
    exactamente con (title_stripped, artist_stripped, mp3_data),
    en ese orden, tal como espera la firma de SongRepository.insert().
    """
    mock_repo = MagicMock()
    mock_repo.insert.return_value = 10
    service = SongService(song_repo=mock_repo)
    audio = b"binary_audio_data"

    service.add_song(" Clean Title ", " Clean Artist ", audio)

    mock_repo.insert.assert_called_once_with("Clean Title", "Clean Artist", audio)
