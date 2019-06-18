from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

app = Flask(__name__)

jwt = JWTManager(app)


#
# from service_app.resources.users import bp as users_bp
# app.register_blueprint(users_bp)
#
# from service_app.resources.auth import bp as auth_bp
# app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return jsonify({
        "text": "dich"
    })



if __name__ == '__main__':
    print(__name__)
    app.run(debug=True)