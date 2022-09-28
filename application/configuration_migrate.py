from datetime import timedelta


class Configuration:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@storageDB/storage"
    # REDIS_HOST = os.environ["REDIS_PORT"]
    REDIS_HOST = "redis"
    REDIS_THREADS_LIST = "products"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
