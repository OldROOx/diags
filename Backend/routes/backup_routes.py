from flask import Blueprint, jsonify, Response, request
from services.backup_service import BackupService
from exceptions import SongNotFoundError, BackupNotFoundError, EmptyAudioError

backup_bp = Blueprint("backups", __name__)
_service  = BackupService()


@backup_bp.route("/api/songs_backup", methods=["GET"])
def list_backups():
    return jsonify(_service.list_backups())


@backup_bp.route("/api/backup/<int:song_id>", methods=["POST"])
def create_backup(song_id: int):
    note      = request.form.get("note", "manual backup")
    backed_by = request.form.get("backed_by", "web-ui")

    try:
        backup_id = _service.backup_song(song_id, note=note, backed_by=backed_by)
    except SongNotFoundError as e:
        return jsonify({"ok": False, "error": str(e)}), 404

    return jsonify({"ok": True, "backup_id": backup_id})


@backup_bp.route("/play_backup/<int:backup_id>", methods=["GET"])
def stream_backup(backup_id: int):
    try:
        backup = _service.get_audio(backup_id)
    except BackupNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except EmptyAudioError as e:
        return jsonify({"error": str(e)}), 404

    return Response(
        backup["mp3_data"],
        mimetype="audio/mpeg",
        headers={"Content-Disposition": f'inline; filename="{backup["title"]}_backup.mp3"'},
    )