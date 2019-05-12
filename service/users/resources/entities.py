from flask_restful import Resource, fields, marshal_with

from service.users.models import User


user_fields = {
    "id": fields.Integer(),
    "username": fields.String(),
}


class UserList(Resource):

    @marshal_with(user_fields)
    def get(self):
        return User.query.all()


class UserDetail(Resource):

    def get(self, user_id):
        pass

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass





