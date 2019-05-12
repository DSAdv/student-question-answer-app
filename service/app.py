from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from flask_sqlalchemy import SQLAlchemy, inspect

from flask_restful import Api, Resource
from flask_restful import abort, reqparse, fields, marshal_with

from flask_migrate import Migrate

from service.config import BaseConfig
from service.users.models import RevokedTokenModel

jwt = JWTManager()
db = SQLAlchemy()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    db.init_app(app)
    jwt.init_app(app)

    migrate = Migrate(app, db)

    from service.users import create_users_blueprint
    app.register_blueprint(create_users_blueprint(), url_prefix="/users")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)