from flask import Flask, send_from_directory
from config import Config
from routes.song_routes   import song_bp
from routes.backup_routes import backup_bp

app = Flask(__name__, static_folder=".", static_url_path="")

app.register_blueprint(song_bp)
app.register_blueprint(backup_bp)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)