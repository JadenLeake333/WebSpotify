class Config(object):
    DEBUG = False
    TESTING = False
    STATIC_FOLDER = 'application/static'
    TEMPLATES_FOLDER = 'application/templates'

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
