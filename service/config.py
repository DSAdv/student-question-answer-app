

class BaseConfig(object):
    SECRET_KEY = "xF8ZN29M-tlPECQSdU662fR8qV-Lnf_G0hGn6J9YTiw"
    SQLALCHEMY_DATABASE_URI = "sqlite:///service.sqlite"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    JWT_SECRET_KEY = "TEdBvTLiYpCTJKcKqu1SDUk1nMbEQ0fSU8CgkNl8a-Q"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']