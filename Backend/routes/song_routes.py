from flask import Blueprint, jsonify, Response
from services.song_service import SongService
from exceptions import SongNotFoundError, EmptyAudioError

song_bp = Blueprint("songs", __name__)
_service = SongService()


@song_bp.route("/api/songs", methods=["GET"])
def list_songs():
    songs = _service.list_songs()
    return jsonify(songs)


@song_bp.route("/play/<song_id>", methods=["GET"])
def stream_song(song_id: str):
    # Validación del parámetro de ruta antes de llegar al service
    try:
        sid = int(song_id)
        if sid <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "El id debe ser un entero positivo."}), 400

    try:
        song = _service.get_audio(sid)
    except SongNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except EmptyAudioError as e:
        return jsonify({"error": str(e)}), 404

    return Response(
        song["mp3_data"],
        mimetype="audio/mpeg",
        headers={"Content-Disposition": f'inline; filename="{song["title"]}.mp3"'},
    )