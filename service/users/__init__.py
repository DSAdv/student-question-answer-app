from flask import Blueprint
from flask_restful import Api
from service.users.resources import auth, entities


def create_users_blueprint():

    api_bp = Blueprint("users", __name__)
    api = Api(api_bp)

    api.add_resource(auth.UserLogin, "/login", endpoint="users:login")
    api.add_resource(auth.UserRegistration, "/register", endpoint="users:register")

    api.add_resource(auth.SecretResource, "/jwt_secret_resource")

    api.add_resource(auth.UserLogoutAccess, '/logout/access')
    api.add_resource(auth.UserLogoutRefresh, '/logout/refresh')
    api.add_resource(auth.TokenRefresh, '/token/refresh')

    api.add_resource(entities.UserDetail, "/detail/<user_id>", endpoint="users:detail")
    api.add_resource(entities.UserList, "/", endpoint="users:list")

    return api_bp
