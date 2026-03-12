# tests/test_app.py
# Pruebas de API de Backups (test_021 a test_030)
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Importar la app después de configurar mocks si es necesario
from app import app


@pytest.fixture
def client():
    """Cliente de prueba Flask."""
    app.config['TESTING'] = True
    return app.test_client()


def _mock_conn_songs_backup(rows):
    """Crea mock de conexión para GET /api/songs_backup."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = rows
    mock_conn.cursor.return_value = mock_cur
    return mock_conn, mock_cur


def _mock_conn_backup_post(song_row=None, lastrowid=42):
    """Crea mock de conexión para POST /api/backup/<id>."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = song_row
    mock_cur.lastrowid = lastrowid
    mock_conn.cursor.return_value = mock_cur
    return mock_conn, mock_cur


@patch('app.mysql.connector.connect')
def test_021_api_backup_retorna_json(mock_connect, client):
    """Ruta: GET /api/songs_backup | JSON | Resultado: Content-Type correcto."""
    mock_conn, mock_cur = _mock_conn_songs_backup([])
    mock_connect.return_value = mock_conn

    response = client.get('/api/songs_backup')

    assert response.status_code == 200
    assert 'application/json' in response.content_type


@patch('app.mysql.connector.connect')
def test_022_api_backup_codigo_200(mock_connect, client):
    """Ruta: GET /api/songs_backup | HTTP 200 | Resultado: Código 200 retornado."""
    mock_conn, mock_cur = _mock_conn_songs_backup([])
    mock_connect.return_value = mock_conn

    response = client.get('/api/songs_backup')

    assert response.status_code == 200


@patch('app.mysql.connector.connect')
def test_023_api_backup_estructura_json(mock_connect, client):
    """Ruta: GET /api/songs_backup | Estructura | Resultado: Todos los campos presentes."""
    dt = datetime(2025, 2, 19, 10, 30, 0)
    rows = [(1, 10, 'Test Song', 'Artist', 'note', 'web-ui', dt)]
    mock_conn, mock_cur = _mock_conn_songs_backup(rows)
    mock_connect.return_value = mock_conn

    response = client.get('/api/songs_backup')
    data = response.get_json()

    assert len(data) == 1
    item = data[0]
    required_fields = ['id', 'original_song_id', 'title', 'artist', 'backup_note', 'backed_up_by', 'backed_up_at']
    for field in required_fields:
        assert field in item, f"Campo '{field}' no presente en la respuesta"


@patch('app.mysql.connector.connect')
def test_024_api_backup_ordenamiento(mock_connect, client):
    """Ruta: GET /api/songs_backup | ORDER BY DESC | Resultado: Ordenados por fecha DESC."""
    mock_conn, mock_cur = _mock_conn_songs_backup([])
    mock_connect.return_value = mock_conn

    client.get('/api/songs_backup')

    call_args = mock_cur.execute.call_args[0][0].upper()
    assert 'ORDER BY' in call_args and 'BACKED_UP_AT' in call_args and 'DESC' in call_args


@patch('app.mysql.connector.connect')
def test_025_api_backup_timestamp_conversion(mock_connect, client):
    """Ruta: GET /api/songs_backup | ISO timestamp | Resultado: Formato ISO retornado."""
    dt = datetime(2025, 2, 19, 10, 30, 0)
    rows = [(1, 10, 'Song', 'Artist', 'note', 'user', dt)]
    mock_conn, mock_cur = _mock_conn_songs_backup(rows)
    mock_connect.return_value = mock_conn

    response = client.get('/api/songs_backup')
    data = response.get_json()

    assert len(data) == 1
    backed_up_at = data[0]['backed_up_at']
    assert '2025-02-19' in backed_up_at
    assert '10:30:00' in backed_up_at or '10:30' in backed_up_at


@patch('app.mysql.connector.connect')
def test_026_api_backup_lista_vacia(mock_connect, client):
    """Ruta: GET /api/songs_backup | Sin backups | Resultado: Array vacío."""
    mock_conn, mock_cur = _mock_conn_songs_backup([])
    mock_connect.return_value = mock_conn

    response = client.get('/api/songs_backup')
    data = response.get_json()

    assert data == []
    assert isinstance(data, list)


@patch('app.mysql.connector.connect')
def test_027_api_backup_cierre_conexion(mock_connect, client):
    """Ruta: GET /api/songs_backup | Cierre | Resultado: Recursos cerrados."""
    mock_conn, mock_cur = _mock_conn_songs_backup([])
    mock_connect.return_value = mock_conn

    client.get('/api/songs_backup')

    mock_cur.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('app.mysql.connector.connect')
def test_028_api_crear_backup_codigo_200(mock_connect, client):
    """Ruta: POST /api/backup/<id> | Crear backup | Resultado: HTTP 200."""
    song_row = (1, 'Test Song', 'Artist', b'mp3_data')
    mock_conn, mock_cur = _mock_conn_backup_post(song_row=song_row, lastrowid=99)
    mock_connect.return_value = mock_conn

    response = client.post('/api/backup/1')

    assert response.status_code == 200


@patch('app.mysql.connector.connect')
def test_029_api_backup_id_invalido_404(mock_connect, client):
    """Ruta: POST /api/backup/<id> | ID inválido | Resultado: HTTP 404."""
    mock_conn, mock_cur = _mock_conn_backup_post(song_row=None)
    mock_connect.return_value = mock_conn

    response = client.post('/api/backup/99999')

    assert response.status_code == 404
    data = response.get_json()
    assert data.get('ok') is False
    assert 'error' in data or 'not found' in data.get('error', '').lower()


@patch('app.mysql.connector.connect')
def test_030_api_crear_backup_retorna_json(mock_connect, client):
    """Ruta: POST /api/backup/<id> | JSON response | Resultado: ok y backup_id."""
    song_row = (1, 'Test Song', 'Artist', b'mp3_data')
    mock_conn, mock_cur = _mock_conn_backup_post(song_row=song_row, lastrowid=42)
    mock_connect.return_value = mock_conn

    response = client.post('/api/backup/1')
    data = response.get_json()

    assert data.get('ok') is True
    assert 'backup_id' in data
    assert data['backup_id'] == 42
