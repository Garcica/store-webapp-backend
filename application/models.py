from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "product_categories"
    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.productId, self.categoryId)


class OrderRequest(database.Model):
    __tablename__ = "order_requests"
    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)
    cost = database.Column(database.Float, nullable=False)
    received = database.Column(database.Integer, nullable=False)
    requested = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.productId, self.orderId)


class Product(database.Model):
    __tablename__ = "products"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    cost = database.Column(database.Float, nullable=False)
    number = database.Column(database.Integer, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=OrderRequest.__table__, back_populates="products")

    def __repr__(self):
        return "({}, {}, {}, {})".format(self.id, self.name, self.cost, self.number)


class Order(database.Model):
    __tablename__ = "orders"
    id = database.Column(database.Integer, primary_key=True)
    cost = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    date = database.Column(database.DateTime, nullable=False)
    user_id = database.Column(database.Integer, nullable=False)

    products = database.relationship("Product", secondary=OrderRequest.__table__, back_populates="orders")

    def __repr__(self):
        return "({}, {}, {}, {})".format(self.id, self.cost, self.status, self.date)


class Category(database.Model):
    __tablename__ = "categories"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return "({}, {})".format(self.id, self.name)
