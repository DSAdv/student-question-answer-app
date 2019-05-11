from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy, inspect
from flask_restful import Api, Resource
from flask_restful import abort, reqparse, fields, marshal_with
from flask_migrate import Migrate

from flask import g
from flask_httpauth import HTTPBasicAuth

from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

api = Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


auth = HTTPBasicAuth()


class UserModel(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(32), index=True)
    name = db.Column(db.String(32))
    surname = db.Column(db.String(32))
    full_group_name = db.Column(db.String(16))
    telegram_id = db.Column(db.String(64))
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = UserModel.query.get(data['id'])
        return user

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<UserModel [{name} {surname}]>".format(
            name=self.name,
            surname=self.surname,
            group=self.full_group_name,
        )


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = UserModel.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = UserModel.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


user_fields = {
    "id": fields.Integer(),
    "username": fields.String(),
    "name": fields.String(),
    "surname": fields.String(),
    "full_group_name": fields.String(),
    "telegram_id": fields.String(),
}

parser = reqparse.RequestParser()
for key in user_fields.keys():
    parser.add_argument(key)


# Resources

class UserLogin(Resource):
    pass


class UserLogout(Resource):
    pass


class UserDetail(Resource):

    @marshal_with(user_fields)
    def get(self, user_id):
        user_data = UserModel.query.filter_by(id=user_id).first()
        if user_data is None:
            abort(404, message="User with ID:{} doesn't exist.".format(user_id))
        return user_data

    @marshal_with(user_fields)
    def put(self, user_id):

        args = parser.parse_args()
        user_data = {
            key: args.get(key) for key in user_fields.keys() if args.get(key, None)
        }
        all_users[user_id].update(user_data), 201
        return all_users[user_id], 201

    def delete(self, user_id):
        pass


class UserListView(Resource):

    @marshal_with(user_fields)
    def get(self):
        return UserModel.query.all()

    @marshal_with(user_fields)
    def post(self):
        args = parser.parse_args()
        user_data = {
            key: args.get(key) for key in user_fields.keys() if args.get(key, None) and key != "id"
        }
        if "name" not in user_data and "surname" not in user_data:
            abort(400, message="Your user data is incorrect add Name and Surname")

        user_data = UserModel(**user_data)
        db.session.add(user_data)
        db.session.commit()
        return UserModel.query \
            .filter_by(name=user_data["name"], surname=user_data["surname"]) \
            .first()


api.add_resource(UserDetail, "/users/<user_id>", endpoint="users")
api.add_resource(UserListView, "/users", endpoint="users:detail")


if __name__ == '__main__':
    app.run(debug=True)



