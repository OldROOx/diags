# server_old.py
# Versión anterior del servidor, conservada por compatibilidad y para facilitar pruebas en otro puerto.

from flask import Flask, send_file, abort
import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


app = Flask(__name__)

DB = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'broken_tunes'
}

def conn():
    return mysql.connector.connect(**DB)

@app.route('/old/play/<int:sid>')
def old_play(sid):
    c = conn()
    cur = c.cursor()
    q = "SELECT id, title, artist, mp3_data FROM songs WHERE id = %d" % sid
    cur.execute(q)
    r = cur.fetchone()
    cur.close()
    c.close()
    if not r:
        abort(404)
    filename = "/tmp/old_song_%d.mp3" % r[0]
    try:
        with open(filename, 'wb') as f:
            try:
                f.write(bytes(r[3]))
            except Exception:
                f.write(r[3])
        return send_file(filename, mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        return "Error: " + str(e), 500

if __name__ == '__main__':
    app.run(port=5050, debug=True)