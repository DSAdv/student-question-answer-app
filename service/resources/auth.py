from flask import request, Blueprint, g
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity,
    create_refresh_token, jwt_refresh_token_required, get_raw_jwt)
from flask_restful import Resource, abort, marshal, marshal_with, Api
from werkzeug.security import generate_password_hash, check_password_hash

from service_app.common.errors import IncorrectRequestBodyError, ExistingUserError
from service_app.resources.users import user_fields


bp = Blueprint("auth", __name__, url_prefix="/auth")
api = Api(bp, prefix="/api/v1")


class Register(Resource):
    @marshal_with(user_fields)
    def post(self):
        if not isinstance(request.json, dict):
            abort(IncorrectRequestBodyError)

        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if connector.db.users.find({"username": username}).count():
            abort(ExistingUserError.code, message=ExistingUserError.message)

        user = {key: request.json.get(key, None) for key in user_fields.keys()}

        if password is None:
            user["password"] = generate_password_hash(user["username"] + user["id"])
        else:
            user["password"] = generate_password_hash(user["password"])
        user["access_token"] = create_access_token(identity=user["username"])
        user["refresh_token"] = create_refresh_token(identity=user["username"])
        connector.db.users.insert(marshal(user, user_fields))
        return user


class Login(Resource):
    def post(self):
        data = request.json
        username = data['username']
        try:
            current_user = connector.db.users.find({"username": username})[0]
        except IndexError as e:
            return {
                "error": {
                    "status": 404,
                    "message": "Unexpected attribute value in field 'username'",
                }
            }

        if current_user["password"] and (
                check_password_hash(current_user["password"], data["password"]) or
                check_password_hash(current_user["password"], generate_password_hash(data["id"]+data["username"]))
        ):
            g.current_user = current_user

            return {
                'access_token': create_access_token(identity=username),
                'refresh_token': create_refresh_token(identity=username),
            }
        else:
            return {'message': 'Wrong credentials'}


class LogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            connector.db.tokens.insert({"jti": jti})
            return {'message': 'Access token has been revoked'}
        except:
            abort(500, message="Something went wrong with your token.")


class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            connector.db.tokens.insert({"jti": jti})
            return {'message': 'Refresh token has been revoked'}
        except:
            abort(500, message="Something went wrong with your token.")


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}


api.add_resource(Register, "/register")
api.add_resource(Login, "/login")

api.add_resource(TokenRefresh, "/get_token")

api.add_resource(LogoutAccess, "/access_token_revoke")
api.add_resource(LogoutRefresh, "/refresh_token_revoke")


from service_app.app import connector