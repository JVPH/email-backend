import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

import config
from app.database.db import db

from flask_cors import CORS

from app.resources.emails import blp as EmailsBlueprint
from app.resources.users import blp as UsersBlueprint


def create_app():
    """
    Create and configure the Flask app.

    Returns:
        Flask app: The configured Flask app instance.
    """
    app = Flask(__name__)
    frontend_url = os.getenv("FRONTEND_URL")
    print(frontend_url)
    CORS(
        app,
        origins=[
            "http://email.techfellowhomegroup8.net",
            "http://ec2-23-22-195-194.compute-1.amazonaws.com",
            "http://23.22.195.194",
        ],
    )
    load_dotenv()
    app.config.from_object(config.get_config())

    db.init_app(app)

    migrate = Migrate(app, db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    jwt = JWTManager(app)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """
        Handle revoked token error.

        Args:
            jwt_header: The JWT header.
            jwt_payload: The JWT payload.

        Returns:
            JSON response: A JSON response indicating the revoked token error.
        """
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """
        Handle expired token error.

        Args:
            jwt_header: The JWT header.
            jwt_payload: The JWT payload.

        Returns:
            JSON response: A JSON response indicating the expired token error.
        """
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """
        Handle invalid token error.

        Args:
            error: The invalid token error.

        Returns:
            JSON response: A JSON response indicating the invalid token error.
        """
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """
        Handle missing token error.

        Args:
            error: The missing token error.

        Returns:
            JSON response: A JSON response indicating the missing token error.
        """
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        """
        Handle not fresh token error.

        Args:
            jwt_header: The JWT header.
            jwt_payload: The JWT payload.

        Returns:
            JSON response: A JSON response indicating the not fresh token error.
        """
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    api.register_blueprint(UsersBlueprint)
    api.register_blueprint(EmailsBlueprint)

    return app
