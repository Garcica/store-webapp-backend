from datetime import timedelta
import os

#databaseUrl = os.environ["DATABASE_URL"]


class Configuration:
    #SQLALCHEMY_DATABASE_URI_2 = f"mysql+pymysql://root:root@/127.0.0.1:3307/authentication"
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@authenticationDB/authentication"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/authentication"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
