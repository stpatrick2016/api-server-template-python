import datetime
import os
import typing
from functools import wraps
from uuid import uuid4

import jwt
from flask import Flask, request, jsonify
from google.auth.transport import requests
from google.oauth2 import id_token
from werkzeug.exceptions import abort

from common import get_logger

logger = get_logger(__name__)


class Session:
    def __init__(self):
        self.id = uuid4().hex
        self.timestamp = datetime.datetime.utcnow()
        self.expiration = datetime.datetime.utcnow()
        self.email: str = ""

    def is_valid(self) -> bool:
        return datetime.datetime.utcnow() < self.expiration


class OidcServer:
    validate_password: typing.Callable[[str, str], bool] = None
    validate_user: typing.Callable[[str], bool] = lambda self, x: True
    issuer = "urn:philip-patrick"
    secret_key: str = uuid4().hex
    access_token_lifetime: datetime.timedelta = datetime.timedelta(hours=1)
    refresh_token_lifetime: datetime.timedelta = datetime.timedelta(days=30)

    __sessions: typing.Dict[str, Session] = {}

    def configure(
        self,
        app: Flask,
        token_endpoint: str = "/token",
        config_endpoint: str = "/.well-known/openid-configuration",
    ):
        app.add_url_rule(token_endpoint, view_func=self._token, methods=["POST"])
        app.add_url_rule(config_endpoint, view_func=self._config, methods=["GET"])
        OidcServer.secret_key = app.secret_key or OidcServer.secret_key

    @staticmethod
    def authorize(f):
        # noinspection PyBroadException
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "Authorization" in request.headers:
                auth_type, token = request.headers["Authorization"].split(None, 1)
                if auth_type == "Bearer":
                    try:
                        jwt.decode(
                            token,
                            key=OidcServer.secret_key,
                            algorithms=["HS256"],
                            options={"require": ["sub", "email", "exp"]},
                        )
                    except Exception as e:
                        logger.info(
                            f"Invalid JWT token passed by {request.remote_addr} to {request.path}. Error: {e}",
                            exc_info=e,
                        )
                        abort(401)
                    return f(*args, **kwargs)
            logger.info("Headers: " + str(request.headers))
            abort(401)

        return decorated_function

    def _token(self):
        grant_type = request.form["grant_type"]
        client_id = request.form["client_id"]

        if grant_type == "password" and self.validate_password:
            email = request.form["username"]
            if self.validate_password(email, request.form["password"]):
                return jsonify(
                    access_token=self._generate_jwt(email),
                    token_type="Bearer",
                    expires_in=self.access_token_lifetime.seconds,
                    scope="openid email",
                    refresh_token=self._save_session(email),
                )
        elif grant_type == "refresh_token" and "refresh_token" in request.form:
            session = self._get_session(request.form["refresh_token"])
            if session and self.validate_user(session.email):
                return jsonify(
                    access_token=self._generate_jwt(session.email),
                    token_type="Bearer",
                    expires_in=self.access_token_lifetime.seconds,
                    scope="openid email",
                    refresh_token=session.id,
                )
        elif grant_type == "authorization_code" and client_id == os.environ.get(
            "GOOGLE_CLIENT_ID"
        ):
            try:
                id_info = id_token.verify_oauth2_token(
                    request.form["code"],
                    requests.Request(),
                    client_id,
                    clock_skew_in_seconds=10,
                )
                email = id_info["email"]
                return jsonify(
                    access_token=self._generate_jwt(email),
                    token_type="Bearer",
                    expires_in=self.access_token_lifetime.seconds,
                    scope="openid email",
                    refresh_token=self._save_session(email),
                    email=email,
                    name=id_info["name"],
                )
            except ValueError as e:
                logger.info(
                    f"Invalid Google id token token passed by {request.remote_addr} to {request.path}. Error: {e}",
                    exc_info=e,
                )

        return "", 401

    def _config(self):
        pass

    def _generate_jwt(self, username: str) -> str:
        return jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + self.access_token_lifetime,
                "iss": self.issuer,
                "iat": datetime.datetime.utcnow(),
                "sub": username,
                "email": username,
            },
            key=OidcServer.secret_key,
            algorithm="HS256",
        )

    def _save_session(self, email: str) -> str:
        session = Session()
        session.expiration = datetime.datetime.utcnow() + self.refresh_token_lifetime
        session.email = email
        self.__sessions[session.id] = session
        return session.id

    def _get_session(self, refresh_token) -> typing.Optional[Session]:
        session = self.__sessions.get(refresh_token)
        if session and not session.is_valid():
            del self.__sessions[refresh_token]
            session = None
        return session


authorize = OidcServer.authorize
