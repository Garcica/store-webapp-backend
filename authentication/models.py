from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class User(database.Model):
    __tablename__ = "users"

    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    first_name = database.Column(database.String(256), nullable=False)
    last_name = database.Column(database.String(256), nullable=False)

    role = database.Column(database.Integer, database.ForeignKey("roles.id"), nullable=False)
    roles = database.relationship("Role", back_populates="users")

    def __repr__(self):
        return "({}, {}, {}, {}, {})".format(self.id, self.email, self.password, self.first_name, self.last_name)


class Role(database.Model):
    __tablename__ = "roles"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    users = database.relationship("User", back_populates="roles")

    def __repr__(self):
        return "({}, {})".format(self.id, self.title)
