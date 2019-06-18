from flask import Blueprint, g
from flask_restful import Api, Resource, fields, marshal_with, request, marshal_with_field, abort, marshal


bp = Blueprint("users", __name__, url_prefix="/users")
api = Api(bp, prefix="/api/v1")


tg_fields = ["id", "username", "first_name", "last_name", "is_bot", "language_code"]


telegram_fields = {
    "username": fields.String(),
    "first_name": fields.String(),
    "last_name": fields.String(),
    "is_bot": fields.Boolean(default=False),
    "language_code": fields.String(),
}


user_fields = {
    "id": fields.Integer(),
    "username": fields.String(),
    "email": fields.String(),
    "first_name": fields.String(),
    "last_name": fields.String(),
    "is_bot": fields.Boolean(default=False),
    "language_code": fields.String(),
    "password": fields.String(),
    "group": fields.Integer(),
    "access_token": fields.String(),
    "refresh_token": fields.String(),
}


class UserDetail(Resource):
    pass


class UserList(Resource):
    @marshal_with(user_fields)
    def get(self):
        return [user for user in connector.db.users.find()]


api.add_resource(UserList, "/")

from service_app.app import connector
