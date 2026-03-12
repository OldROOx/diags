"""
test_exceptions.py – Tests T1 a T6
Pruebas unitarias para el módulo exceptions.py.

Verifica la jerarquía de herencia, los atributos y los mensajes de cada
excepción del dominio Broken Tunes.
"""

import pytest
from exceptions import (
    BrokenTunesError,
    SongNotFoundError,
    BackupNotFoundError,
    EmptyAudioError,
    DuplicateSongError,
)


# ─────────────────────────────────────────────────────────────────────────────
# T1 – BrokenTunesError es subclase de Exception
# ─────────────────────────────────────────────────────────────────────────────
def test_T1_broken_tunes_error_es_exception():
    """
    T1: BrokenTunesError debe ser una subclase directa de la clase base
    Exception de Python, garantizando que el dominio puede usar un bloque
    'except BrokenTunesError' que captura todos los errores propios.
    """
    assert issubclass(BrokenTunesError, Exception)


# ─────────────────────────────────────────────────────────────────────────────
# T2 – SongNotFoundError hereda de BrokenTunesError
# ─────────────────────────────────────────────────────────────────────────────
def test_T2_song_not_found_error_hereda_de_broken_tunes_error():
    """
    T2: SongNotFoundError debe ser subclase de BrokenTunesError para que
    cualquier manejador genérico del dominio pueda capturarla sin conocer
    el tipo concreto.
    """
    assert issubclass(SongNotFoundError, BrokenTunesError)


# ─────────────────────────────────────────────────────────────────────────────
# T3 – SongNotFoundError almacena song_id y tiene mensaje correcto
# ─────────────────────────────────────────────────────────────────────────────
def test_T3_song_not_found_error_atributo_y_mensaje():
    """
    T3: Al instanciar SongNotFoundError(99), la excepción debe:
      - Almacenar el id en el atributo .song_id
      - Incluir el id en el mensaje str() de la excepción
    Esto permite que los manejadores de errores extraigan el id sin parsear.
    """
    error = SongNotFoundError(99)
    assert error.song_id == 99
    assert "99" in str(error)


# ─────────────────────────────────────────────────────────────────────────────
# T4 – BackupNotFoundError almacena backup_id y tiene mensaje correcto
# ─────────────────────────────────────────────────────────────────────────────
def test_T4_backup_not_found_error_atributo_y_mensaje():
    """
    T4: Al instanciar BackupNotFoundError(42), la excepción debe:
      - Ser subclase de BrokenTunesError
      - Almacenar el id en el atributo .backup_id
      - Incluir el id en el mensaje str()
    """
    error = BackupNotFoundError(42)
    assert issubclass(BackupNotFoundError, BrokenTunesError)
    assert error.backup_id == 42
    assert "42" in str(error)


# ─────────────────────────────────────────────────────────────────────────────
# T5 – EmptyAudioError tiene mensaje que incluye el nombre del recurso
# ─────────────────────────────────────────────────────────────────────────────
def test_T5_empty_audio_error_incluye_nombre_recurso():
    """
    T5: EmptyAudioError("canción id=7") debe:
      - Ser subclase de BrokenTunesError
      - Incluir el nombre del recurso en el mensaje, para que los logs
        identifiquen qué elemento no tenía audio.
    """
    resource = "canción id=7"
    error = EmptyAudioError(resource)
    assert issubclass(EmptyAudioError, BrokenTunesError)
    assert resource in str(error)


# ─────────────────────────────────────────────────────────────────────────────
# T6 – DuplicateSongError incluye título y artista en el mensaje
# ─────────────────────────────────────────────────────────────────────────────
def test_T6_duplicate_song_error_incluye_titulo_y_artista():
    """
    T6: DuplicateSongError("Bohemian Rhapsody", "Queen") debe:
      - Ser subclase de BrokenTunesError
      - Incluir tanto el título como el artista en el mensaje str(),
        para que el usuario o el log identifique cuál fue el duplicado.
    """
    error = DuplicateSongError("Bohemian Rhapsody", "Queen")
    assert issubclass(DuplicateSongError, BrokenTunesError)
    assert "Bohemian Rhapsody" in str(error)
    assert "Queen" in str(error)
