# BROKEN TUNES - DOCUMENTACIÓN SIMPLE

## 1. Contexto del Negocio
**Cliente:** Bar "El Sótano"  
**Necesidad:** Rockola digital para uso interno, que funcione en la máquina del bar.  
**Restricciones clave:**
- Offline: debe sonar sin Internet.
- Portabilidad: poder moverlo entre PCs con pocos archivos.
- Interfaz táctil y control de velocidad (pedido del DJ).

---

## 2. Solución (resumen rápido)
- Backend: Python
- Base de datos: MySQL
- Web: HTML + JS
- MP3s pueden almacenarse en la base de datos para simplificar mover el sistema.

Equipo (roles):
- Frontend — interfaz y estilos.
- Backend — API y base de datos.
- Documentación — instrucciones y notas.

---

## 3. Cómo ejecutar el proyecto
1. Poner los archivos del proyecto en la máquina que será la rockola.
2. Importar el SQL (archivo `backup_db.sql`) con la herramienta que prefieras.
3. Asegurarte de tener Python 3 y ejecutar algo como `pip install flask mysql-connector-python`.
4. Ejecutar el servidor: `python app.py`.
5. Abrir en el navegador la dirección `http://localhost:5000` desde la tablet/PC del bar.

Si algo no funciona, revisar la base de datos, las dependencias y si la app puede escuchar la base de datos. Hay varias formas de arreglarlo; prueba y error suele servir.

Credenciales por defecto (demo):
- Usuario: `admin`
- Password: `1234`

---

## 4. Añadir canciones (manera sencilla)
- Convertir mp3 a base64 y poner el archivo en la carpeta `uploads/`, luego ejecutar el script `upload_to_db.py`.
- También puedes insertar directam. con SQL usando `FROM_BASE64(...)` si sabes hacerlo.
- Si el nombre del archivo contiene `backup`, el uploader lo mete en la tabla de backups.

---

## 5. Uso básico
- Abrir la UI, elegir una canción y presionar "Play".
- Ajustar la velocidad con el control en pantalla.
- Para hacer copia rápida de una canción, usar "Backup" en la UI.

---

## 6. Archivos importantes
- `backup_db.sql` — base de datos y datos de ejemplo.
- `app.py` — servidor principal.
- `index.html` — interfaz.
- `upload_to_db.py` — script para subir desde `uploads/`.

---