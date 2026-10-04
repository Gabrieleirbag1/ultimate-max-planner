from flask import Flask
from flask_cors import CORS

from api.routes import bp
from config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=app.config["CORS_ORIGINS"].split(","))
    app.register_blueprint(bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5200, debug=True)
