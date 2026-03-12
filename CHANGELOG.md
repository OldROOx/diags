<a name="top"></a>
# CHANGELOG - BROKEN TUNES

**Versión actual:** v0.1.0

Este archivo registra cambios importantes del proyecto. Añade una entrada nueva arriba cada vez que completes un cambio relevante.

---

## ÍNDICE
- [Cómo usar este archivo](#como-usar-este-archivo)  
- [Versionamiento y reglas para cambiar versión](#versionamiento-y-reglas-para-cambiar-versi%C3%B3n)  
- [Historial de cambios](#historial-de-cambios)  
- [Plantilla para nuevas entradas](#plantilla-para-nuevas-entradas)  
- [Preguntas frecuentes (FAQ)](#preguntas-frecuentes-faq)  

---

## Cómo usar este archivo
1. Al terminar un cambio importante, añade una entrada nueva arriba en "Historial de cambios".
2. Sigue el formato de la plantilla (versión/fecha, tipo, breve detalle, archivos tocados, autor, issue).
3. Cuando el cambio requiera actualizar la versión, sigue las reglas en la sección "Versionamiento...".
4. No borres entradas antiguas; sólo añade nuevas.

---

## Versionamiento y reglas para cambiar versión

Usamos un esquema simple tipo SemVer: MAJOR.MINOR.PATCH (ej. 0.1.0).

- Bump PATCH (ej. 0.1.1) = Corrección de bugs o cambios pequeños que no añaden features.
- Bump MINOR (ej. 0.2.0) = Nueva funcionalidad que no rompe compatibilidad (feature visible, nuevos endpoints, UI importante).
- Bump MAJOR (ej. 1.0.0) = Cambio incompatible que rompe flujos existentes, reestructura DB o cambia contratos de API.

Reglas prácticas:
- Si el cambio es solo CSS o texto, solo añade entrada y no cambies versión (opcional: PATCH).
- Si agregas una nueva API o endpoint, sube MINOR.
- Si arreglas un bug visible o typo en lógica, sube PATCH.
- Si cambias la estructura de la base de datos o rompes endpoints, sube MAJOR.

Cómo cambiar la versión en el changelog:
- Edita la línea "Versión actual" al inicio con la nueva versión.
- Añade una entrada nueva con la versión y fecha en la parte superior del "Historial de cambios".

(Nota: el versionamiento en este archivo es manual; si usan git tags, pueden agregar tags aparte.)

---

## Historial de cambios

### [v1.0.0] - 2026-01-14 - Versión inicial / MVP
- **Tipo:** Agregado  
- **Detalle:** app.py (endpoints básicos: /, /api/songs, /play/<id>, /login); UI básica; esquema inicial.  
- **Archivos tocados:** `app.py`, `index.html`, `backup_db.sql`  
- **Autor:** Backend / Frontend (roles)  
- **Issue:** N/A

### [v0.3.0] - 2026-01-14 - Backups y UI mejorada
- **Tipo:** Cambiado / Agregado  
- **Detalle:** Tabla `songs_backup` definida explícitamente; endpoints de backup; UI con sección Backups y botón Backup.  
- **Archivos tocados:** `backup_db.sql`, `app.py`, `index.html`  
- **Autor:** Backend / Frontend  
- **Issue:** N/A

### [v0.2.0] - 2026-01-14 - Datos de ejemplo ampliados
- **Tipo:** Agregado  
- **Detalle:** Muchas canciones de ejemplo añadidas (duplicados, caracteres especiales, etc.) para pruebas.  
- **Archivos tocados:** `backup_db.sql`  
- **Autor:** Documentación / Backend  
- **Issue:** N/A

### [v0.1.0] - 2026-01-14 - Scripts y tablas auxiliares
- **Tipo:** Agregado  
- **Detalle:** `upload_to_db.py`, `server_old.py`, `file_index` y otros scripts/utilidades añadidos.  
- **Archivos tocados:** `upload_to_db.py`, `server_old.py`, `backup_db.sql`  
- **Autor:** Backend  
- **Issue:** N/A

(Agrega nuevas entradas aquí arriba cada vez que hagas cambios.)

---

## Plantilla para nuevas entradas

Pega esto arriba cuando termines un cambio. Rellena `ISSUE_LINK` con la URL del issue/task que motivó el cambio (si no existe, poner `N/A`).

```
### [vX.Y.Z] - AAAA-MM-DD - Título corto
- **Tipo:** Agregado/Cambiado/Arreglado/Eliminado
- **Detalle:** Una frase clara de qué se hizo.
- **Archivos tocados:** archivo1, archivo2
- **Autor:** rol o iniciales (ej. Frontend, Backend, Docs)
- **Issue:** ISSUE_LINK
```

Notas sobre el campo Issue:
- Use un enlace a la issue en el tracker del proyecto (ej. `https://github.com/owner/repo/issues/123`) o al ticket en la herramienta que usen.
- Si no hubo un issue formal, poner `N/A` o un link a la discusión relevante.

---

## Preguntas frecuentes (FAQ)

- ¿Quién anota el changelog?  
  Quien haga el cambio (o la persona que mergea el PR). Si fueron varios, pongan los roles o iniciales.

- ¿Cada commit necesita entrada?  
  No. Solo cambios relevantes: features, fixes, cambios en DB, etc.

- ¿Dónde actualizo la versión?  
  Edita "Versión actual" arriba y usa la plantilla para añadir la entrada. Sigue las reglas de versionamiento.

- ¿Qué hago si olvidé anotar algo?  
  Añádelo cuando recuerdes; mejor tarde que nunca.

- ¿Puedo borrar o reescribir entradas?  
  No, mantenlo como historial completo.

- ¿Necesito pruebas o CI para anotar?  
  No obligatorio. Si tienes CI/PR, añade la referencia (opcional).

[Ir al principio](#top)

---

## Pequeños consejos prácticos
- Mantén frases cortas y concretas.
- Sé consistente en los tipos (Agregado/Cambiado/Arreglado/Eliminado).
- Añadir el rol o nombre del autor y el enlace al issue ayuda a rastrear decisiones.

---

Si quieres, puedo:
- Añadir un pequeño script opcional que ponga la plantilla nueva arriba (solo crea la plantilla, no rellena campos), o
- Generar un ejemplo de entrada con un issue real ficticio para que el equipo vea cómo queda. ¿Cuál prefieres?