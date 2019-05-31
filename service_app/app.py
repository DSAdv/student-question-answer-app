from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api, fields
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = ""
app.config["SECRET_KEY"] = ""

connector = PyMongo(app)
jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return bool(connector.db.tokens.find({"jti": jti}))


from service_app.resources.users import bp as users_bp
app.register_blueprint(users_bp)

from service_app.resources.auth import bp as auth_bp
app.register_blueprint(auth_bp)



if __name__ == '__main__':
    print(__name__)
    app.run(debug=True)