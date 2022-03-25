import os
from uuid import uuid4

from flask import Flask
from flask_cors import CORS
from waitress import serve

from models.json_encoder import CustomJsonEncoder
from security.oidc import OidcServer

app = Flask(__name__)
CORS(app)
oidc = OidcServer()


@app.route("/")
def root_stub():
    return "", 200


def validate_user(username: str) -> bool:
    return (
        True if username in ["saint.patricius@gmail.com", "netkka@gmail.com"] else False
    )


if __name__ == "__main__":
    app.json_encoder = CustomJsonEncoder
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    app.secret_key = os.environ.get("SECRET_KEY") or uuid4().hex
    oidc.configure(app)
    oidc.validate_user = validate_user

    serve(app, host="0.0.0.0", port=5000)
