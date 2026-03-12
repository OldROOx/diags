# Servidor Flask para BROKEN TUNES (implementación monolítica)
from flask import Flask, jsonify, Response, send_from_directory, request, abort
# Servidor Flask para BROKEN TUNES (implementación monolítica con Logging para Mantenimiento)
import os
import logging
import mysql.connector
import time

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, Response, send_from_directory, request, abort

logging.basicConfig(
    filename='mantenimiento_bt.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')

@@ -19,119 +25,159 @@
    'database': os.getenv('DB_NAME')
}


def get_db():
    conn = mysql.connector.connect(**DB)
    return conn
    try:
        conn = mysql.connector.connect(**DB)
        return conn
    except Exception as e:
        # Registro crítico: Si la DB falla, el mantenimiento correctivo empieza aquí
        logger.critical(f"ERROR CRÍTICO DE CONEXIÓN A DB: {str(e)}")
        raise


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/songs')
def api_songs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, artist FROM songs WHERE mp3_data IS NOT NULL AND LENGTH(mp3_data) > 0")
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({'id': r[0], 'title': r[1], 'artist': r[2]})
    cur.close()
    conn.close()
    return jsonify(result)
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, title, artist FROM songs WHERE mp3_data IS NOT NULL AND LENGTH(mp3_data) > 0")
        rows = cur.fetchall()
        result = []
        for r in rows:
            result.append({'id': r[0], 'title': r[1], 'artist': r[2]})
        cur.close()
        conn.close()
        logger.info(f"Consulta exitosa de biblioteca: {len(result)} canciones listadas.")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Fallo al obtener canciones: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/songs_backup')
def api_songs_backup():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, original_song_id, title, artist, backup_note, backed_up_by, backed_up_at FROM songs_backup ORDER BY backed_up_at DESC")
    rows = cur.fetchall()
    out = []
    for r in rows:
        out.append({
            'id': r[0],
            'original_song_id': r[1],
            'title': r[2],
            'artist': r[3],
            'backup_note': r[4],
            'backed_up_by': r[5],
            'backed_up_at': r[6].isoformat() if hasattr(r[6], 'isoformat') else r[6]
        })
    cur.close()
    conn.close()
    return jsonify(out)
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, original_song_id, title, artist, backup_note, backed_up_by, backed_up_at FROM songs_backup ORDER BY backed_up_at DESC")
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                'id': r[0],
                'original_song_id': r[1],
                'title': r[2],
                'artist': r[3],
                'backup_note': r[4],
                'backed_up_by': r[5],
                'backed_up_at': r[6].isoformat() if hasattr(r[6], 'isoformat') else r[6]
            })
        cur.close()
        conn.close()
        logger.info("Consulta de backups realizada.")
        return jsonify(out)
    except Exception as e:
        logger.error(f"Error en consulta de backups: {str(e)}")
        return jsonify({"error": "Error al cargar backups"}), 500


@app.route('/api/backup/<int:song_id>', methods=['POST'])
def api_backup_song(song_id):
    # Crear una copia en songs_backup de la canción indicada
    backed_by = request.form.get('backed_by', 'web-ui')
    note = request.form.get('note', 'manual backup')
    conn = get_db()
    cur = conn.cursor()
    # Obtener la canción original
    cur.execute("SELECT id, title, artist, mp3_data FROM songs WHERE id = %s", (song_id,))
    row = cur.fetchone()
    if not row:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, title, artist, mp3_data FROM songs WHERE id = %s", (song_id,))
        row = cur.fetchone()

        if not row:
            logger.warning(f"Intento de backup fallido: Canción ID {song_id} no encontrada.")
            cur.close()
            conn.close()
            return jsonify({'ok': False, 'error': 'song not found'}), 404

        original_id, title, artist, mp3_blob = row[0], row[1], row[2], row[3]
        try:
            mp3_bytes = bytes(mp3_blob)
        except Exception:
            mp3_bytes = mp3_blob

        insert_q = (
            "INSERT INTO songs_backup (original_song_id, title, artist, mp3_data, backup_note, backed_up_by, backed_up_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, NOW())")
        cur.execute(insert_q, (original_id, title, artist, mp3_bytes, note, backed_by))
        conn.commit()
        backup_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({'ok': False, 'error': 'song not found'}), 404
    original_id, title, artist, mp3_blob = row[0], row[1], row[2], row[3]
    try:
        mp3_bytes = bytes(mp3_blob)
    except Exception:
        mp3_bytes = mp3_blob
    # Insertar en songs_backup
    insert_q = ("INSERT INTO songs_backup (original_song_id, title, artist, mp3_data, backup_note, backed_up_by, backed_up_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW())")
    cur.execute(insert_q, (original_id, title, artist, mp3_bytes, note, backed_by))
    conn.commit()
    backup_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'ok': True, 'backup_id': backup_id})

        logger.info(f"BACKUP CREADO: ID {backup_id} para canción '{title}' (ID original: {original_id}).")
        return jsonify({'ok': True, 'backup_id': backup_id})
    except Exception as e:
        logger.error(f"Fallo en proceso de backup para canción {song_id}: {str(e)}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/play/<id>')
def play_song(id):
    conn = get_db()
    cur = conn.cursor()
    # Consulta construida directamente para mantener el código directo y fácil de seguir
    query = "SELECT * FROM songs WHERE id = " + id
    cur.execute(query)
    row = cur.fetchone()
    if not row:
    try:
        conn = get_db()
        cur = conn.cursor()
        query = "SELECT * FROM songs WHERE id = " + id
        cur.execute(query)
        row = cur.fetchone()
        if not row:
            logger.warning(f"Intento de reproducción fallido: Canción ID {id} no existe.")
            cur.close()
            conn.close()
            abort(404)

        mp3_blob = row[3]
        data = bytes(mp3_blob) if isinstance(mp3_blob, (bytearray, bytes)) else mp3_blob
        cur.close()
        conn.close()
        abort(404)
    mp3_blob = row[3]
    try:
        data = bytes(mp3_blob)
    except Exception:
        data = mp3_blob
    cur.close()
    conn.close()
    return Response(data, mimetype='audio/mpeg',
                    headers={"Content-Disposition": "inline; filename=\"%s.mp3\"" % row[1]})

        logger.info(f"Reproduciendo canción: {row[1]} (ID: {id})")
        return Response(data, mimetype='audio/mpeg',
                        headers={"Content-Disposition": f"inline; filename=\"{row[1]}.mp3\""})
    except Exception as e:
        logger.error(f"Error al reproducir canción ID {id}: {str(e)}")
        return "Error interno", 500


@app.route('/play_backup/<int:backup_id>')
def play_backup(backup_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, artist, mp3_data FROM songs_backup WHERE id = %s", (backup_id,))
    row = cur.fetchone()
    if not row:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, title, artist, mp3_data FROM songs_backup WHERE id = %s", (backup_id,))
        row = cur.fetchone()
        if not row:
            logger.warning(f"Backup no encontrado para reproducción: ID {backup_id}")
            cur.close()
            conn.close()
            abort(404)

        data = bytes(row[3]) if isinstance(row[3], (bytearray, bytes)) else row[3]
        cur.close()
        conn.close()
        abort(404)
    try:
        data = bytes(row[3])
    except Exception:
        data = row[3]
    cur.close()
    conn.close()
    return Response(data, mimetype='audio/mpeg',
                    headers={"Content-Disposition": "inline; filename=\"%s_backup.mp3\"" % row[1]})

        logger.info(f"Reproduciendo backup: {row[1]} (ID Backup: {backup_id})")
        return Response(data, mimetype='audio/mpeg',
                        headers={"Content-Disposition": f"inline; filename=\"{row[1]}_backup.mp3\""})
    except Exception as e:
        logger.error(f"Error al reproducir backup ID {backup_id}: {str(e)}")
        return "Error interno", 500


if __name__ == '__main__':
    logger.info("Iniciando servidor BROKEN TUNES - Puerto 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)