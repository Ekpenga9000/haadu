class BaseConfig:
    SECRET_KEY='21stFeb94$'
    ADMIN_EMAIL='myemail@ymail.com'

class Testconfig(BaseConfig):
    ADMIN_EMAIL='test@yahoo.com'

class LiveConfig(BaseConfig):
    ADMIN_EMAIL='live@yahoo.com'