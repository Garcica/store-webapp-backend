import csv
import io

from flask import Flask, request, Response, jsonify
from configuration_migrate import Configuration
from models import database
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request
from functools import wraps
from redis import Redis
import json

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


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


def check_value(value):
    try:
        float(value)
    except ValueError:
        return False
    if float(value) > 0:
        return True
    else:
        return False


@application.route("/update", methods=["POST"])
@roleCheck(role="3")
def update():
    file = request.files.get("file", None)
    if not file:
        return Response(json.dumps({"message": "Field file is missing."}), status=400)

    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    redis = Redis(host=Configuration.REDIS_HOST)

    products = []
    cnt = 0

    for row in reader:
        if len(row) < 4 or len(row) > 4:
            return Response(json.dumps({"message": "Incorrect number of values on line {}.".format(cnt)}), status=400)

        if not check_value(row[2]):
            return Response(json.dumps({"message": "Incorrect quantity on line {}.".format(cnt)}), status=400)

        if not check_value(row[3]):
            return Response(json.dumps({"message": "Incorrect price on line {}.".format(cnt)}), status=400)

        line = "{},{},{},{}".format(row[0], row[1], row[2], row[3])
        products.append(line)
        cnt = cnt + 1

    with Redis(host=Configuration.REDIS_HOST) as redis:
        for line in products:
            redis.publish(channel="storekeeper", message=line)

    return Response(json.dumps({"message": "Update successful!"}), status=200)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
