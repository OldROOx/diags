"""
conftest.py – Configuración compartida de Pytest para el Backend.

Agrega el directorio Backend al sys.path para que los módulos del backend
(services, repositories, exceptions, etc.) sean importables desde los tests.
También provee fixtures reutilizables como el cliente de prueba de Flask.
"""

import sys
import os

# Insertamos la ruta de Backend/ al sys.path para que los imports funcionen
# sin necesidad de instalar el paquete.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app as flask_app


@pytest.fixture
def client():
    """
    Fixture que crea un cliente de prueba de Flask.
    Activa el modo TESTING para que los errores se propaguen correctamente.
    """
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client
