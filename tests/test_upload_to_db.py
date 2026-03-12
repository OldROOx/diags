# tests/test_upload_to_db.py
# Pruebas para upload_to_db.py
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

# Importar después de posibles mocks
import upload_to_db


@patch('upload_to_db.mysql.connector.connect')
def test_upload_to_db_get_db_conecta(mock_connect):
    """Verifica que get_db retorna una conexión."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    conn = upload_to_db.get_db()

    assert conn is mock_conn
    mock_connect.assert_called_once()


@patch('upload_to_db.get_db')
def test_upload_to_db_sin_carpeta_uploads(mock_get_db):
    """Si uploads/ no existe, main no procesa archivos."""
    with patch.object(upload_to_db, 'UPLOAD_DIR', tempfile.mktemp()):
        with patch('builtins.print') as mock_print:
            upload_to_db.main()

    mock_get_db.assert_not_called()
    mock_print.assert_called()
    call_str = str(mock_print.call_args)
    assert 'uploads' in call_str.lower() or 'Crea' in call_str


@patch('upload_to_db.get_db')
def test_upload_to_db_procesa_archivo_backup(mock_get_db):
    """Archivos con 'backup' en el nombre se insertan en songs_backup."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    with tempfile.TemporaryDirectory() as tmpdir:
        backup_file = os.path.join(tmpdir, 'my_song_backup.b64')
        with open(backup_file, 'wb') as f:
            f.write(b'U29tZQ==')  # base64 de "Some"

        with patch.object(upload_to_db, 'UPLOAD_DIR', tmpdir):
            with patch('builtins.print'):
                upload_to_db.main()

    mock_cur.execute.assert_called()
    call_args = mock_cur.execute.call_args[0][0]
    assert 'songs_backup' in call_args


@patch('upload_to_db.get_db')
def test_upload_to_db_procesa_archivo_normal(mock_get_db):
    """Archivos sin 'backup' se insertan en songs."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    with tempfile.TemporaryDirectory() as tmpdir:
        normal_file = os.path.join(tmpdir, 'song.mp3')
        with open(normal_file, 'wb') as f:
            f.write(b'fake_mp3_data')

        with patch.object(upload_to_db, 'UPLOAD_DIR', tmpdir):
            with patch('builtins.print'):
                upload_to_db.main()

    mock_cur.execute.assert_called()
    call_args = mock_cur.execute.call_args[0][0]
    assert 'songs' in call_args


@patch('upload_to_db.get_db')
def test_upload_to_db_cierra_conexion(mock_get_db):
    """Verifica que se cierran cursor y conexión al finalizar."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(upload_to_db, 'UPLOAD_DIR', tmpdir):
            with patch('builtins.print'):
                upload_to_db.main()

    mock_cur.close.assert_called_once()
    mock_conn.close.assert_called_once()
