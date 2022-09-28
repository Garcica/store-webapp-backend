import re
import json

from flask import jsonify, request, Flask, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt, JWTManager, create_access_token, create_refresh_token, \
    jwt_required, get_jwt_identity
from functools import wraps

from sqlalchemy import and_

from configuration_migrate import Configuration
from models import database, User

application = Flask(__name__)
application.config.from_object(Configuration)


def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if role == claims["roles"]:
                return function(*arguments, **keywordArguments)
            else:
                return jsonify({
                    "msg": "Missing Authorization Header"
                }), 401

        return decorator

    return innerRole


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/register", methods=["POST"])
def register():
    first_name = request.json.get("forename", "")
    last_name = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    role = request.json.get("isCustomer", None)

    if len(first_name) == 0:
        return Response(json.dumps({"message": "Field forename is missing."}), status=400)

    if len(last_name) == 0:
        return Response(json.dumps({"message": "Field surname is missing."}), status=400)

    if len(email) == 0:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    if len(password) == 0:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    if role is None:
        return Response(json.dumps({"message": "Field isCustomer is missing."}), status=400)

    # Checking if email is valid
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(email_regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    # Checking if password is valid
    if not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) \
            or not any(char.islower() for char in password):
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    # Checking if email is unique
    user = User.query.filter(User.email == email).first()
    if user:
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    if role:
        user_role = 2
    else:
        user_role = 3

    user = User(email=email, password=password, first_name=first_name, last_name=last_name, role=user_role)
    database.session.add(user)
    database.session.commit()

    return Response(json.dumps({"message": "You have successfully registrated!"}), status=200)


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    if len(password) == 0:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    # Checking if email is valid
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(email_regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if not user:
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    additionalClaims = {
        "forename": user.first_name,
        "surname": user.last_name,
        "email": user.email,
        "roles": str(user.role)
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken)


@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid!"


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "email": refreshClaims["email"],
        "roles": refreshClaims["roles"]
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims)), 200


@application.route("/delete", methods=["POST"])
@roleCheck(role="1")
def delete():
    email = request.json.get("email", "")

    if len(email) == 0:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    # Checking if email is valid
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(email_regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(User.email == email).first()

    if not user:
        return Response(json.dumps({"message": "Unknown user."}), status=400)

    database.session.delete(user)
    database.session.commit()

    return Response(json.dumps({"message": "User successfully deleted."}), status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)
