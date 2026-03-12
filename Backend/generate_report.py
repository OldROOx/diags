"""
generate_report.py
==================
Script que ejecuta las 50 pruebas unitarias con pytest, captura los logs
de ejecución y genera un PDF completo con:

  - Portada del proyecto
  - Tabla de los 50 casos de prueba (id, módulo, descripción)
  - Resultado detallado de cada test (PASSED / FAILED / ERROR)
  - Logs completos de ejecución de pytest

Dependencias necesarias:
    pip install reportlab pytest

Uso:
    cd Backend/
    python generate_report.py
"""

import subprocess
import sys
import os
import re
from datetime import datetime

# ─── Constantes ──────────────────────────────────────────────────────────────

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BACKEND_DIR, "tests")
OUTPUT_PDF = os.path.join(BACKEND_DIR, "reporte_pruebas.pdf")

# Descripción corta de cada uno de los 50 tests para la tabla del PDF
TEST_CATALOG = [
    # (id, archivo, nombre_funcion, descripcion_corta)
    ("T01", "test_exceptions", "test_T1_broken_tunes_error_es_exception",
     "BrokenTunesError es subclase de Exception"),
    ("T02", "test_exceptions", "test_T2_song_not_found_error_hereda_de_broken_tunes_error",
     "SongNotFoundError hereda de BrokenTunesError"),
    ("T03", "test_exceptions", "test_T3_song_not_found_error_atributo_y_mensaje",
     "SongNotFoundError almacena song_id y mensaje correcto"),
    ("T04", "test_exceptions", "test_T4_backup_not_found_error_atributo_y_mensaje",
     "BackupNotFoundError almacena backup_id y mensaje correcto"),
    ("T05", "test_exceptions", "test_T5_empty_audio_error_incluye_nombre_recurso",
     "EmptyAudioError incluye el nombre del recurso en el mensaje"),
    ("T06", "test_exceptions", "test_T6_duplicate_song_error_incluye_titulo_y_artista",
     "DuplicateSongError incluye título y artista en el mensaje"),
    ("T07", "test_config",     "test_T7_db_params_devuelve_dict",
     "Config.db_params() devuelve un dict"),
    ("T08", "test_config",     "test_T8_db_params_contiene_claves_requeridas",
     "Config.db_params() contiene host, user, password, database"),
    ("T09", "test_config",     "test_T9_debug_por_defecto_es_false",
     "Config.DEBUG por defecto es False"),
    ("T10", "test_config",     "test_T10_host_por_defecto_es_0000",
     "Config.HOST por defecto es '0.0.0.0'"),
    ("T11", "test_config",     "test_T11_port_por_defecto_es_5000_y_es_entero",
     "Config.PORT por defecto es 5000 (tipo int)"),
    ("T12", "test_song_service", "test_T12_list_songs_devuelve_lista_vacia",
     "SongService.list_songs() → [] cuando repo no tiene canciones"),
    ("T13", "test_song_service", "test_T13_list_songs_devuelve_datos_del_repo",
     "SongService.list_songs() devuelve datos sin modificar del repo"),
    ("T14", "test_song_service", "test_T14_list_songs_llama_get_all_del_repo",
     "SongService.list_songs() delega exactamente a repo.get_all()"),
    ("T15", "test_song_service", "test_T15_get_audio_devuelve_dict_cuando_song_existe",
     "SongService.get_audio() devuelve dict completo con audio válido"),
    ("T16", "test_song_service", "test_T16_get_audio_lanza_song_not_found_cuando_no_existe",
     "SongService.get_audio() → SongNotFoundError si repo devuelve None"),
    ("T17", "test_song_service", "test_T17_get_audio_lanza_empty_audio_cuando_mp3_data_es_bytes_vacios",
     "SongService.get_audio() → EmptyAudioError si mp3_data = b''"),
    ("T18", "test_song_service", "test_T18_get_audio_lanza_empty_audio_cuando_mp3_data_es_none",
     "SongService.get_audio() → EmptyAudioError si mp3_data = None"),
    ("T19", "test_song_service", "test_T19_add_song_devuelve_id_del_repo",
     "SongService.add_song() devuelve el id generado por repo.insert()"),
    ("T20", "test_song_service", "test_T20_add_song_lanza_duplicate_cuando_integrity_error",
     "SongService.add_song() convierte IntegrityError → DuplicateSongError"),
    ("T21", "test_song_service", "test_T21_add_song_strip_titulo",
     "SongService.add_song() aplica strip() al título"),
    ("T22", "test_song_service", "test_T22_add_song_strip_artista",
     "SongService.add_song() aplica strip() al artista"),
    ("T23", "test_song_service", "test_T23_add_song_llama_insert_con_args_correctos",
     "SongService.add_song() llama repo.insert() con args normalizados"),
    ("T24", "test_backup_service", "test_T24_list_backups_devuelve_lista_vacia",
     "BackupService.list_backups() → [] cuando no hay backups"),
    ("T25", "test_backup_service", "test_T25_list_backups_devuelve_datos_del_repo",
     "BackupService.list_backups() devuelve datos del backup_repo"),
    ("T26", "test_backup_service", "test_T26_backup_song_lanza_song_not_found_cuando_no_existe",
     "BackupService.backup_song() → SongNotFoundError si canción no existe"),
    ("T27", "test_backup_service", "test_T27_backup_song_devuelve_backup_id",
     "BackupService.backup_song() devuelve el backup_id generado"),
    ("T28", "test_backup_service", "test_T28_backup_song_pasa_original_song_id_correcto",
     "BackupService.backup_song() pasa original_song_id correcto"),
    ("T29", "test_backup_service", "test_T29_backup_song_copia_titulo_y_artista",
     "BackupService.backup_song() copia título y artista de la canción"),
    ("T30", "test_backup_service", "test_T30_backup_song_copia_mp3_data",
     "BackupService.backup_song() copia mp3_data de la canción"),
    ("T31", "test_backup_service", "test_T31_backup_song_pasa_note_y_backed_by",
     "BackupService.backup_song() pasa note y backed_by al repo"),
    ("T32", "test_backup_service", "test_T32_get_audio_backup_devuelve_dict_cuando_existe",
     "BackupService.get_audio() devuelve dict de backup con audio"),
    ("T33", "test_backup_service", "test_T33_get_audio_backup_lanza_backup_not_found_cuando_no_existe",
     "BackupService.get_audio() → BackupNotFoundError si backup es None"),
    ("T34", "test_backup_service", "test_T34_get_audio_backup_lanza_empty_audio_cuando_vacio",
     "BackupService.get_audio() → EmptyAudioError si mp3_data = b''"),
    ("T35", "test_backup_service", "test_T35_store_uploaded_backup_devuelve_id",
     "BackupService.store_uploaded_backup() devuelve backup_id"),
    ("T36", "test_backup_service", "test_T36_store_uploaded_backup_usa_original_song_id_none",
     "BackupService.store_uploaded_backup() usa original_song_id=None"),
    ("T37", "test_song_routes",   "test_T37_get_songs_devuelve_200",
     "GET /api/songs devuelve HTTP 200"),
    ("T38", "test_song_routes",   "test_T38_get_songs_devuelve_lista_json",
     "GET /api/songs devuelve array JSON"),
    ("T39", "test_song_routes",   "test_T39_get_songs_devuelve_datos_del_servicio",
     "GET /api/songs devuelve datos del servicio sin modificar"),
    ("T40", "test_song_routes",   "test_T40_play_song_devuelve_200_y_audio_mpeg",
     "GET /play/<id> válido → HTTP 200 con Content-Type audio/mpeg"),
    ("T41", "test_song_routes",   "test_T41_play_song_con_id_no_entero_devuelve_400",
     "GET /play/abc → HTTP 400 (id no numérico)"),
    ("T42", "test_song_routes",   "test_T42_play_song_con_id_cero_devuelve_400",
     "GET /play/0 → HTTP 400 (id = 0 es inválido)"),
    ("T43", "test_song_routes",   "test_T43_play_song_cuando_no_existe_devuelve_404",
     "GET /play/<id> canción no encontrada → HTTP 404"),
    ("T44", "test_backup_routes", "test_T44_get_backups_devuelve_200",
     "GET /api/songs_backup devuelve HTTP 200"),
    ("T45", "test_backup_routes", "test_T45_get_backups_devuelve_lista_json",
     "GET /api/songs_backup devuelve array JSON de backups"),
    ("T46", "test_backup_routes", "test_T46_post_backup_retorna_ok_true_y_backup_id",
     "POST /api/backup/<id> → {'ok': True, 'backup_id': N}"),
    ("T47", "test_backup_routes", "test_T47_post_backup_cuando_cancion_no_existe_retorna_404",
     "POST /api/backup/<id> canción inexistente → HTTP 404 con ok=False"),
    ("T48", "test_backup_routes", "test_T48_post_backup_pasa_note_del_formulario",
     "POST /api/backup/<id> pasa form data 'note' y 'backed_by' al servicio"),
    ("T49", "test_backup_routes", "test_T49_play_backup_devuelve_200_y_audio_mpeg",
     "GET /play_backup/<id> válido → HTTP 200 con Content-Type audio/mpeg"),
    ("T50", "test_backup_routes", "test_T50_play_backup_cuando_no_existe_devuelve_404",
     "GET /play_backup/<id> backup no encontrado → HTTP 404"),
]


# ─── Ejecución de pytest ──────────────────────────────────────────────────────

def run_pytest() -> tuple[str, int]:
    """
    Ejecuta pytest en el directorio de tests con salida verbose.
    Retorna (output_completo: str, codigo_retorno: int).
    """
    print("=" * 60)
    print("  Ejecutando 50 pruebas unitarias con pytest...")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--no-header",
            "--color=no",
        ],
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
    )

    output = result.stdout + ("\n" + result.stderr if result.stderr.strip() else "")
    print(output)
    return output, result.returncode


# ─── Parseo del output de pytest ─────────────────────────────────────────────

def parse_results(output: str) -> dict[str, str]:
    """
    Parsea el output de pytest y devuelve un dict {nombre_funcion: status}
    donde status es 'PASSED', 'FAILED', 'ERROR' o 'UNKNOWN'.
    """
    results = {}
    for line in output.splitlines():
        # Líneas típicas: "tests/test_foo.py::test_bar PASSED"
        match = re.search(r"::(test_\w+)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)", line)
        if match:
            results[match.group(1)] = match.group(2)
    return results


# ─── Generación del PDF ───────────────────────────────────────────────────────

def generate_pdf(pytest_output: str, return_code: int, results: dict[str, str]):
    """
    Genera el PDF con portada, tabla de 50 tests y logs completos de pytest.
    Requiere: pip install reportlab
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, PageBreak,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        print("\n[ERROR] 'reportlab' no está instalado.")
        print("  Instálalo con: pip install reportlab")
        print("  Luego vuelve a ejecutar: python generate_report.py")
        return

    # ── Estilos ──────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a237e"),
        spaceAfter=10,
        alignment=TA_CENTER,
    )
    style_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=13,
        textColor=colors.HexColor("#37474f"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    style_seccion = ParagraphStyle(
        "Seccion",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1a237e"),
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4,
    )
    style_normal = ParagraphStyle(
        "Normal2",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        spaceAfter=4,
    )
    style_code = ParagraphStyle(
        "Code",
        parent=styles["Code"],
        fontSize=7.5,
        leading=11,
        fontName="Courier",
        spaceAfter=2,
        leftIndent=0,
        backColor=colors.HexColor("#f5f5f5"),
    )
    style_footer = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_RIGHT,
    )

    # Colores de estado
    COLOR_PASSED = colors.HexColor("#c8e6c9")
    COLOR_FAILED = colors.HexColor("#ffcdd2")
    COLOR_UNKNOWN = colors.HexColor("#fff9c4")
    COLOR_HEADER = colors.HexColor("#1a237e")
    COLOR_HEADER_TXT = colors.white
    COLOR_ROW_ALT = colors.HexColor("#f5f5f5")

    # ── Construcción del documento ────────────────────────────────────────────
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    passed_count = sum(1 for v in results.values() if v == "PASSED")
    failed_count = sum(1 for v in results.values() if v in ("FAILED", "ERROR"))
    total_detectados = len(results)
    estado_global = "EXITOSO ✓" if return_code == 0 else "CON FALLOS ✗"

    # ── PORTADA ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("Reporte de Pruebas Unitarias", style_titulo))
    story.append(Paragraph("Broken Tunes – Backend", style_subtitulo))
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
    story.append(Spacer(1, 0.5 * cm))

    resumen_data = [
        ["Campo", "Valor"],
        ["Fecha de ejecución", fecha],
        ["Total de pruebas", "50"],
        ["Pruebas detectadas", str(total_detectados)],
        ["Pruebas PASSED", str(passed_count)],
        ["Pruebas FAILED / ERROR", str(failed_count)],
        ["Estado global", estado_global],
        ["Framework", "pytest"],
        ["Lenguaje", "Python 3"],
    ]

    resumen_table = Table(resumen_data, colWidths=[6 * cm, 9 * cm])
    resumen_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER),
        ("TEXTCOLOR",  (0, 0), (-1, 0), COLOR_HEADER_TXT),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ROW_ALT]),
        ("GRID",       (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(resumen_table)
    story.append(PageBreak())

    # ── TABLA DE 50 CASOS DE PRUEBA ───────────────────────────────────────────
    story.append(Paragraph("Catálogo de 50 Casos de Prueba", style_seccion))
    story.append(Spacer(1, 0.2 * cm))

    header = ["ID", "Módulo", "Función de Test", "Descripción", "Resultado"]
    table_data = [header]

    for tid, modulo, funcion, descripcion in TEST_CATALOG:
        status = results.get(funcion, "NO DETECTADO")
        table_data.append([tid, modulo, funcion, descripcion, status])

    col_widths = [1.1 * cm, 3.5 * cm, 5.5 * cm, 6.5 * cm, 2.0 * cm]
    catalog_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Estilos base
    ts = TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), COLOR_HEADER),
        ("TEXTCOLOR",   (0, 0), (-1, 0), COLOR_HEADER_TXT),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 7),
        ("LEADING",     (0, 0), (-1, -1), 10),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.grey),
        ("ALIGN",       (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ROW_ALT]),
    ])

    # Colorear filas según resultado
    for i, (tid, _, funcion, _) in enumerate(TEST_CATALOG, start=1):
        status = results.get(funcion, "NO DETECTADO")
        if status == "PASSED":
            ts.add("BACKGROUND", (-1, i), (-1, i), COLOR_PASSED)
        elif status in ("FAILED", "ERROR"):
            ts.add("BACKGROUND", (-1, i), (-1, i), COLOR_FAILED)
        else:
            ts.add("BACKGROUND", (-1, i), (-1, i), COLOR_UNKNOWN)

    catalog_table.setStyle(ts)
    story.append(catalog_table)
    story.append(PageBreak())

    # ── LOGS COMPLETOS DE PYTEST ──────────────────────────────────────────────
    story.append(Paragraph("Logs Completos de Ejecución de pytest", style_seccion))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Ejecutado el {fecha} | Código de retorno: {return_code}",
        style_normal,
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Dividir el output en líneas y agregar cada una como párrafo monoespaciado
    max_chars = 110  # caracteres por línea antes de truncar
    for raw_line in pytest_output.splitlines():
        # Truncar líneas muy largas para que quepan en el PDF
        if len(raw_line) > max_chars:
            raw_line = raw_line[:max_chars] + "…"
        # Escapar caracteres especiales de XML/ReportLab
        safe_line = (
            raw_line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        ) or " "  # párrafo vacío si la línea es vacía

        # Colorear líneas de resultado
        if "PASSED" in raw_line:
            color = "#2e7d32"
        elif "FAILED" in raw_line or "ERROR" in raw_line:
            color = "#c62828"
        elif raw_line.startswith("PASSED") or "passed" in raw_line.lower():
            color = "#2e7d32"
        else:
            color = "#212121"

        story.append(Paragraph(
            f'<font color="{color}">{safe_line}</font>',
            style_code,
        ))

    # ── Construir PDF ─────────────────────────────────────────────────────────
    doc.build(story)
    print(f"\n[OK] PDF generado: {OUTPUT_PDF}")


# ─── Punto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Ejecutar pytest
    output, returncode = run_pytest()

    # 2. Parsear resultados
    results = parse_results(output)

    passed = sum(1 for v in results.values() if v == "PASSED")
    failed = sum(1 for v in results.values() if v in ("FAILED", "ERROR"))
    print(f"\nResumen: {passed} PASSED | {failed} FAILED | {len(results)} detectados de 50")

    # 3. Generar PDF
    print("\nGenerando PDF del reporte...")
    generate_pdf(output, returncode, results)
