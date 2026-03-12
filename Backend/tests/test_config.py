"""
test_config.py – Tests T7 a T11
Pruebas unitarias para el módulo config.py.

Verifica que Config exponga los parámetros de conexión correctos y que
los valores por defecto de configuración sean los esperados cuando no
se definen variables de entorno.
"""

import pytest
from config import Config


# ─────────────────────────────────────────────────────────────────────────────
# T7 – Config.db_params() devuelve un diccionario
# ─────────────────────────────────────────────────────────────────────────────
def test_T7_db_params_devuelve_dict():
    """
    T7: Config.db_params() debe retornar un objeto de tipo dict.
    Las librerías de conexión MySQL esperan un diccionario de parámetros;
    si el tipo es incorrecto, la conexión fallaría en tiempo de ejecución.
    """
    result = Config.db_params()
    assert isinstance(result, dict)


# ─────────────────────────────────────────────────────────────────────────────
# T8 – Config.db_params() contiene las claves requeridas por mysql-connector
# ─────────────────────────────────────────────────────────────────────────────
def test_T8_db_params_contiene_claves_requeridas():
    """
    T8: El diccionario devuelto por Config.db_params() debe contener
    exactamente las claves 'host', 'user', 'password' y 'database',
    que son las que mysql-connector-python requiere para abrir una conexión.
    """
    params = Config.db_params()
    claves_requeridas = {"host", "user", "password", "database"}
    assert claves_requeridas.issubset(params.keys())


# ─────────────────────────────────────────────────────────────────────────────
# T9 – Config.DEBUG por defecto es False
# ─────────────────────────────────────────────────────────────────────────────
def test_T9_debug_por_defecto_es_false():
    """
    T9: Config.DEBUG debe ser False cuando FLASK_DEBUG no está definido o
    no es exactamente 'true'. Arrancar en modo debug en producción expone
    el debugger interactivo, por lo que el default seguro es False.
    """
    # El valor actual debe ser booleano (no string)
    assert isinstance(Config.DEBUG, bool)
    # Si no se sobreescribió en el entorno, el default es False
    import os
    if os.getenv("FLASK_DEBUG", "false").lower() != "true":
        assert Config.DEBUG is False


# ─────────────────────────────────────────────────────────────────────────────
# T10 – Config.HOST por defecto es "0.0.0.0"
# ─────────────────────────────────────────────────────────────────────────────
def test_T10_host_por_defecto_es_0000():
    """
    T10: Config.HOST debe ser '0.0.0.0' cuando FLASK_HOST no está definido.
    Escuchar en todas las interfaces permite que el servidor sea accesible
    desde fuera del contenedor en entornos Docker/CI.
    """
    import os
    if os.getenv("FLASK_HOST") is None:
        assert Config.HOST == "0.0.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# T11 – Config.PORT por defecto es 5000 y es entero
# ─────────────────────────────────────────────────────────────────────────────
def test_T11_port_por_defecto_es_5000_y_es_entero():
    """
    T11: Config.PORT debe ser de tipo int (no string) con valor 5000 por defecto.
    Flask.run() requiere un entero; si fuera string lanzaría TypeError al inicio.
    """
    assert isinstance(Config.PORT, int)
    import os
    if os.getenv("FLASK_PORT") is None:
        assert Config.PORT == 5000
