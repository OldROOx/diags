"""
test_song_routes.py – Tests T37 a T43
Pruebas de integración ligera para routes/song_routes.py.

Se usa el cliente de prueba de Flask (fixture 'client' de conftest.py)
y se parchea el _service a nivel de módulo con unittest.mock.patch
para evitar acceso real a base de datos.
"""

import pytest
from unittest.mock import MagicMock, patch

from exceptions import SongNotFoundError, EmptyAudioError


# ─────────────────────────────────────────────────────────────────────────────
# T37 – GET /api/songs devuelve HTTP 200
# ─────────────────────────────────────────────────────────────────────────────
def test_T37_get_songs_devuelve_200(client):
    """
    T37: Una petición GET a /api/songs debe retornar código HTTP 200 (OK)
    cuando el servicio devuelve una lista (incluso vacía). Verifica que la
    ruta está registrada y responde correctamente.
    """
    mock_svc = MagicMock()
    mock_svc.list_songs.return_value = []

    with patch("routes.song_routes._service", mock_svc):
        response = client.get("/api/songs")

    assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# T38 – GET /api/songs devuelve una lista JSON
# ─────────────────────────────────────────────────────────────────────────────
def test_T38_get_songs_devuelve_lista_json(client):
    """
    T38: La respuesta de GET /api/songs debe ser un JSON de tipo lista (array),
    no un objeto. El frontend espera iterar sobre un array de canciones.
    """
    songs = [{"id": 1, "title": "A", "artist": "B"}]
    mock_svc = MagicMock()
    mock_svc.list_songs.return_value = songs

    with patch("routes.song_routes._service", mock_svc):
        response = client.get("/api/songs")

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# T39 – GET /api/songs devuelve los datos del servicio sin modificar
# ─────────────────────────────────────────────────────────────────────────────
def test_T39_get_songs_devuelve_datos_del_servicio(client):
    """
    T39: La ruta /api/songs debe serializar y devolver exactamente lo que
    retorna el servicio, incluyendo todos los campos (id, title, artist).
    No debe filtrar ni transformar los datos.
    """
    songs = [
        {"id": 1, "title": "Song One", "artist": "Artist One"},
        {"id": 2, "title": "Song Two", "artist": "Artist Two"},
    ]
    mock_svc = MagicMock()
    mock_svc.list_songs.return_value = songs

    with patch("routes.song_routes._service", mock_svc):
        response = client.get("/api/songs")

    data = response.get_json()
    assert data == songs


# ─────────────────────────────────────────────────────────────────────────────
# T40 – GET /play/<id> con canción válida devuelve HTTP 200 y audio/mpeg
# ─────────────────────────────────────────────────────────────────────────────
def test_T40_play_song_devuelve_200_y_audio_mpeg(client):
    """
    T40: GET /play/1 con una canción válida debe retornar HTTP 200 con
    Content-Type 'audio/mpeg', indicando que se está haciendo streaming
    del archivo MP3.
    """
    song = {"id": 1, "title": "Rock Classic", "artist": "Band", "mp3_data": b"fake_mp3_bytes"}
    mock_svc = MagicMock()
    mock_svc.get_audio.return_value = song

    with patch("routes.song_routes._service", mock_svc):
        response = client.get("/play/1")

    assert response.status_code == 200
    assert "audio/mpeg" in response.content_type


# ─────────────────────────────────────────────────────────────────────────────
# T41 – GET /play/<id_no_entero> devuelve HTTP 400
# ─────────────────────────────────────────────────────────────────────────────
def test_T41_play_song_con_id_no_entero_devuelve_400(client):
    """
    T41: GET /play/abc (id no numérico) debe retornar HTTP 400 (Bad Request)
    con un mensaje de error en JSON, ya que el id debe ser un entero positivo.
    La validación ocurre en la ruta antes de llamar al servicio.
    """
    with patch("routes.song_routes._service", MagicMock()):
        response = client.get("/play/abc")

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


# ─────────────────────────────────────────────────────────────────────────────
# T42 – GET /play/0 devuelve HTTP 400
# ─────────────────────────────────────────────────────────────────────────────
def test_T42_play_song_con_id_cero_devuelve_400(client):
    """
    T42: GET /play/0 debe retornar HTTP 400 porque los ids de base de datos
    son auto-increment y empiezan en 1. Un id=0 es lógicamente inválido.
    La ruta valida que sid > 0 antes de consultar el servicio.
    """
    with patch("routes.song_routes._service", MagicMock()):
        response = client.get("/play/0")

    assert response.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# T43 – GET /play/<id> cuando la canción no existe devuelve HTTP 404
# ─────────────────────────────────────────────────────────────────────────────
def test_T43_play_song_cuando_no_existe_devuelve_404(client):
    """
    T43: GET /play/999 cuando el servicio lanza SongNotFoundError debe retornar
    HTTP 404 (Not Found) con un JSON que contenga el campo 'error'.
    Permite que el cliente distinga entre id inválido (400) y no encontrado (404).
    """
    mock_svc = MagicMock()
    mock_svc.get_audio.side_effect = SongNotFoundError(999)

    with patch("routes.song_routes._service", mock_svc):
        response = client.get("/play/999")

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
