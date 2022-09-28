from flask import Flask, jsonify, request, Response
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from sqlalchemy import and_
from datetime import datetime
from configuration_migrate import Configuration
from models import database, Category, Product, ProductCategory, Order, OrderRequest
from functools import wraps

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


@application.route("/search", methods=["GET"])
@roleCheck(role="2")
def search():
    product = request.args.get("name", None)
    category = request.args.get("category", None)

    products = []
    categories = []

    if category and product:
        categories = Category.query.join(ProductCategory).join(Product).filter(
            and_(
                *[
                    Category.name.like(f"%{category}%"),
                    Product.name.like(f"%{product}%")
                ]
            )
        ).group_by(Category.id).with_entities(Category.name).all()

        products = Product.query.join(ProductCategory).join(Category).filter(
            and_(
                *[
                    Product.name.like(f"%{product}%"),
                    Category.name.like(f"%{category}%")
                ]
            )
        ).group_by(Product.id).all()

    if product and not category:
        categories = Category.query.join(ProductCategory).join(Product).filter(
            and_(
                *[
                    Product.name.like(f"%{product}%")
                ]
            )
        ).group_by(Category.id).with_entities(Category.name).all()
        products = Product.query.join(ProductCategory).join(Category).filter(
            and_(
                *[
                    Product.name.like(f"%{product}%")
                ]
            )
        ).group_by(Product.id).all()

    if category and not product:
        categories = Category.query.join(ProductCategory).join(Product).filter(
            and_(
                *[
                    Category.name.like(f"%{category}%")
                ]
            )
        ).group_by(Category.id).with_entities(Category.name).all()
        products = Product.query.join(ProductCategory).join(Category).filter(
            and_(
                *[
                    Category.name.like(f"%{category}%")
                ]
            )
        ).group_by(Product.id).all()

    if not product and not category:
        categories = Category.query.with_entities(Category.name).all()
        products = Product.query.all()

    json_categories = []

    for category in categories:
        json_categories.append(category[0])

    json_products = []
    for product in products:
        product_categories = []
        for product_category in product.categories:
            product_categories.append(product_category.name)
        json_products.append({
            "categories": product_categories,
            "id": product.id,
            "name": product.name,
            "price": product.cost,
            "quantity": product.number
        })

    result = {
        "categories": json_categories,
        "products": json_products
    }

    return jsonify(result)


@application.route("/order", methods=["POST"])
@roleCheck(role="2")
def order():
    order_requests = request.json.get("requests", "")

    if len(order_requests) == 0:
        return Response(json.dumps({"message": "Field requests is missing."}), 400)

    cnt = 0
    for req in order_requests:
        if req.get("id", "") == "":
            return Response(json.dumps({"message": "Product id is missing for request number {}.".format(cnt)}),
                            400)

        if req.get("quantity", "") == "":
            return Response(json.dumps({"message": "Product quantity is missing for request number {}.".format(cnt)}),
                            400)

        try:
            product_id = int(req['id'])
        except ValueError:
            return Response(json.dumps({"message": "Invalid product id for request number {}.".format(cnt)}),
                            400)

        if product_id <= 0:
            return Response(json.dumps({"message": "Invalid product id for request number {}.".format(cnt)}),
                            400)

        try:
            product_quantity = int(req['quantity'])
        except ValueError:
            return Response(json.dumps({"message": "Invalid product quantity for request number {}.".format(cnt)}),
                            400)

        if product_quantity <= 0:
            return Response(json.dumps({"message": "Invalid product quantity for request number {}.".format(cnt)}),
                            400)

        product = Product.query.filter(Product.id == product_id).first()

        if product is None:
            return Response(json.dumps({"message": "Invalid product for request number {}.".format(cnt)}),
                            400)

        cnt = cnt + 1

    requested_order = Order(cost=0, status="PENDING", date=datetime.today(), user_id=1)
    database.session.add(requested_order)
    database.session.commit()

    order_cost = 0
    can_ship = True

    for req in order_requests:
        product = Product.query.filter(Product.id == req['id']).first()
        order_cost = float(order_cost) + float(product.cost) * float(req['quantity'])
        order_req = OrderRequest(productId=req['id'], orderId=requested_order.id, cost=product.cost, received=0,
                                 requested=req['quantity'])

        if product.number >= req['quantity']:
            product.number = product.number - req["quantity"]
            order_req.received = order_req.requested
        else:
            can_ship = False
            order_req.received = product.number
            product.number = 0

        database.session.add(order_req)
        database.session.commit()

    if can_ship:
        requested_order.status = "COMPLETE"

    requested_order.cost = order_cost
    database.session.commit()

    return Response(json.dumps({"id": requested_order.id}), 200)


@application.route("/status", methods=["GET"])
@roleCheck(role="2")
def status():
    user_id = 1

    orders = Order.query.filter(Order.user_id == user_id).all()

    order_history = []

    for order in orders:
        products_from_order = OrderRequest.query.filter(OrderRequest.orderId == order.id).all()
        products = []

        for product_order in products_from_order:
            product_name = Product.query.filter(Product.id == product_order.productId).first().name
            categories_query = ProductCategory.query.filter(ProductCategory.productId == product_order.productId).all()

            categories = []

            for cat in categories_query:
                category = Category.query.filter(Category.id == cat.categoryId).first()
                categories.append(category.name)

            products.append({
                "categories": categories,
                "name": product_name,
                "price": product_order.cost,
                "received": product_order.received,
                "requested": product_order.requested
            })

        order_history.append({
            "products": products,
            "price": order.cost,
            "status": order.status,
            "timestamp": order.date
        })

    return Response(json.dumps({"orders": order_history}, default=str), 200)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
