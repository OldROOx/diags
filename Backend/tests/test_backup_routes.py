"""
test_backup_routes.py – Tests T44 a T50
Pruebas de integración ligera para routes/backup_routes.py.

Se usa el cliente de prueba de Flask (fixture 'client' de conftest.py)
y se parchea routes.backup_routes._service con mocks para evitar BD real.
"""

import pytest
from unittest.mock import MagicMock, patch

from exceptions import SongNotFoundError, BackupNotFoundError, EmptyAudioError


# ─────────────────────────────────────────────────────────────────────────────
# T44 – GET /api/songs_backup devuelve HTTP 200
# ─────────────────────────────────────────────────────────────────────────────
def test_T44_get_backups_devuelve_200(client):
    """
    T44: Una petición GET a /api/songs_backup debe retornar HTTP 200 (OK)
    cuando el servicio devuelve una lista de backups (incluso vacía).
    Verifica que la ruta de listado de backups está registrada y funciona.
    """
    mock_svc = MagicMock()
    mock_svc.list_backups.return_value = []

    with patch("routes.backup_routes._service", mock_svc):
        response = client.get("/api/songs_backup")

    assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# T45 – GET /api/songs_backup devuelve la lista de backups en JSON
# ─────────────────────────────────────────────────────────────────────────────
def test_T45_get_backups_devuelve_lista_json(client):
    """
    T45: La respuesta de GET /api/songs_backup debe ser un array JSON con los
    datos de backups que retorna el servicio, incluyendo todos los campos.
    """
    backups = [
        {
            "id": 1, "original_song_id": 5, "title": "Rock Song",
            "artist": "Band", "backup_note": "manual", "backed_up_by": "user",
            "backed_up_at": "2024-01-15T10:00:00"
        }
    ]
    mock_svc = MagicMock()
    mock_svc.list_backups.return_value = backups

    with patch("routes.backup_routes._service", mock_svc):
        response = client.get("/api/songs_backup")

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# T46 – POST /api/backup/<id> crea el backup y retorna ok=True con backup_id
# ─────────────────────────────────────────────────────────────────────────────
def test_T46_post_backup_retorna_ok_true_y_backup_id(client):
    """
    T46: POST /api/backup/1 debe crear el backup llamando al servicio y retornar
    un JSON con {'ok': True, 'backup_id': <id>} y HTTP 200. Verifica el flujo
    completo de creación de backup desde la ruta hasta la respuesta.
    """
    mock_svc = MagicMock()
    mock_svc.backup_song.return_value = 99

    with patch("routes.backup_routes._service", mock_svc):
        response = client.post("/api/backup/1")

    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["backup_id"] == 99


# ─────────────────────────────────────────────────────────────────────────────
# T47 – POST /api/backup/<id> cuando la canción no existe retorna 404 con ok=False
# ─────────────────────────────────────────────────────────────────────────────
def test_T47_post_backup_cuando_cancion_no_existe_retorna_404(client):
    """
    T47: Si el servicio lanza SongNotFoundError, POST /api/backup/<id> debe
    retornar HTTP 404 con JSON {'ok': False, 'error': '...'}, permitiendo que
    el cliente distinga una creación exitosa de un fallo por canción inexistente.
    """
    mock_svc = MagicMock()
    mock_svc.backup_song.side_effect = SongNotFoundError(777)

    with patch("routes.backup_routes._service", mock_svc):
        response = client.post("/api/backup/777")

    assert response.status_code == 404
    data = response.get_json()
    assert data["ok"] is False
    assert "error" in data


# ─────────────────────────────────────────────────────────────────────────────
# T48 – POST /api/backup/<id> pasa el 'note' del formulario al servicio
# ─────────────────────────────────────────────────────────────────────────────
def test_T48_post_backup_pasa_note_del_formulario(client):
    """
    T48: POST /api/backup/1 con form data {'note': 'backup urgente'} debe
    pasar ese valor como kwarg 'note' al servicio.backup_song(). Garantiza
    que los parámetros del formulario se propagan correctamente al servicio.
    """
    mock_svc = MagicMock()
    mock_svc.backup_song.return_value = 10

    with patch("routes.backup_routes._service", mock_svc):
        client.post("/api/backup/1", data={"note": "backup urgente", "backed_by": "devops"})

    call_kwargs = mock_svc.backup_song.call_args[1]
    assert call_kwargs["note"] == "backup urgente"
    assert call_kwargs["backed_by"] == "devops"


# ─────────────────────────────────────────────────────────────────────────────
# T49 – GET /play_backup/<id> retorna HTTP 200 y audio/mpeg cuando existe
# ─────────────────────────────────────────────────────────────────────────────
def test_T49_play_backup_devuelve_200_y_audio_mpeg(client):
    """
    T49: GET /play_backup/1 con un backup válido que tiene audio debe retornar
    HTTP 200 con Content-Type 'audio/mpeg'. Verifica el streaming de backups
    de forma análoga al streaming de canciones (T40).
    """
    backup = {"id": 1, "title": "Backup Track", "mp3_data": b"backup_audio_bytes"}
    mock_svc = MagicMock()
    mock_svc.get_audio.return_value = backup

    with patch("routes.backup_routes._service", mock_svc):
        response = client.get("/play_backup/1")

    assert response.status_code == 200
    assert "audio/mpeg" in response.content_type


# ─────────────────────────────────────────────────────────────────────────────
# T50 – GET /play_backup/<id> cuando el backup no existe retorna HTTP 404
# ─────────────────────────────────────────────────────────────────────────────
def test_T50_play_backup_cuando_no_existe_devuelve_404(client):
    """
    T50: GET /play_backup/999 cuando el servicio lanza BackupNotFoundError debe
    retornar HTTP 404 con JSON {'error': '...'}, análogo al test T43 para canciones.
    Garantiza manejo consistente de errores de recursos no encontrados.
    """
    mock_svc = MagicMock()
    mock_svc.get_audio.side_effect = BackupNotFoundError(999)

    with patch("routes.backup_routes._service", mock_svc):
        response = client.get("/play_backup/999")

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
