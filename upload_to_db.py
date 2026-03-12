# upload_to_db.py
# Herramienta para subir archivos desde uploads/ a la base de datos.
# Si el nombre del archivo contiene "backup" se guardará en songs_backup,
# sino se catalogará en file_index.

import os
import base64
import mysql.connector

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

import os 
from dotenv import load_dotenv

load_dotenv()

DB = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')

}

UPLOAD_DIR = 'uploads'

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def main():
    if not os.path.isdir(UPLOAD_DIR):
        print("Crea la carpeta uploads/ y coloca archivos .b64 o .mp3 ahí.")
        return
    files = os.listdir(UPLOAD_DIR)
    conn = get_db()
    cur = conn.cursor()
    for f in files:
        path = os.path.join(UPLOAD_DIR, f)
        if os.path.isdir(path):
            continue
        print("Procesando", f)
        try:
            with open(path, 'rb') as fh:
                data = fh.read()
            # intentamos decodificar si es base64 textual
            decoded = None
            try:
                decoded = base64.b64decode(data)
            except Exception:
                decoded = data
            is_backup = 'backup' in f.lower()
            if is_backup:
                # Insertar directamente en songs_backup para simplificar restauraciones locales
                q = ("INSERT INTO songs_backup (original_song_id, title, artist, mp3_data, backup_note, backed_up_by, backed_up_at) "
                     "VALUES (%s, %s, %s, %s, %s, %s, NOW())")
                # Nombre de archivo usado para título/artist por conveniencia
                title = f
                artist = 'uploader'
                cur.execute(q, (None, title, artist, decoded, 'uploaded backup file', 'upload_to_db'))
                conn.commit()
                print("Insertado en songs_backup:", f)
            else:
                # CORRECCIÓN: Insertar en 'songs' para que aparezca en la biblioteca principal
                q = ("INSERT INTO songs (title, artist, mp3_data, created_at) "
                     "VALUES (%s, %s, %s, NOW())")
                # Usamos el nombre del archivo como título y 'uploader' como artista por defecto
                title = f.replace('.mp3', '').replace('.b64', '')
                artist = 'Nuevas Subidas' 
                
                cur.execute(q, (title, artist, decoded))
                conn.commit()
                print("✅ Insertado en la biblioteca principal (songs):", f)
                
        except Exception as e:
            print("Error procesando", f, ":", e)
    cur.close()
    conn.close()
    print("Hecho. Revisa las tablas file_index y songs_backup.")

if __name__ == '__main__':
    main()