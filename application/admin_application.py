import json

from flask import Flask, jsonify, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt, JWTManager
from functools import wraps
from sqlalchemy import func
from configuration_migrate import Configuration
from models import database, Product, OrderRequest, Category, ProductCategory

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


@application.route("/productStatistics", methods=["GET"])
@roleCheck(role="1")
def productStatistics():
    all_products = Product.query.all()
    statistics = []

    for product in all_products:
        order_requests = OrderRequest.query.filter(OrderRequest.productId == product.id).all()

        requested = 0
        not_shipped = 0

        for order in order_requests:
            requested = requested + order.requested
            not_shipped = not_shipped + order.requested - order.received

        if requested + not_shipped != 0:
            statistics.append({
                "name": product.name,
                "sold": requested,
                "waiting": not_shipped
            })

    return Response(json.dumps({"statistics": statistics}), 200)


@application.route("/categoryStatistics", methods=["GET"])
@roleCheck(role="1")
def categoryStatistics():
    statistics = []

    categories = Category.query.outerjoin(ProductCategory).outerjoin(Product) \
        .outerjoin(OrderRequest).group_by(Category.id) \
        .order_by(func.sum(OrderRequest.requested).desc()).order_by(Category.name)

    for category in categories:
        statistics.append(category.name)

    return Response(json.dumps({"statistics": statistics}), 200)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
