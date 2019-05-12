from flask_restful import Resource
from flask_restful import fields, marshal_with, reqparse, abort
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity,
    create_refresh_token, jwt_refresh_token_required, get_raw_jwt)

from service.users.models import User, RevokedTokenModel

user_access_fields = {
    "message": fields.String(),
    "access_token": fields.String(),
    "refresh_token": fields.String()
}

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)


class UserRegistration(Resource):

    @marshal_with(user_access_fields)
    def post(self):
        args = parser.parse_args()
        username = args.get("username")
        password = args.get("password")

        if User.find_by_username(username):
            return {'message': 'User {} already exists'.format(username)}

        new_user = User(username=username)
        new_user.password = password

        try:
            new_user.save()

            return {
                "message": "User {} was created successful.".format(username),
                "access_token": create_access_token(identity=username),
                "refresh_token": create_refresh_token(identity=username),
            }
        except Exception as e:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):

    @marshal_with(user_access_fields)
    def post(self):
        args = parser.parse_args()
        username = args['username']
        current_user = User.find_by_username(username)

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(username)}

        if current_user.verify_password(args.get("password")):
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': create_access_token(identity=username),
                'refresh_token': create_refresh_token(identity=username),
            }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.save()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}


class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }
