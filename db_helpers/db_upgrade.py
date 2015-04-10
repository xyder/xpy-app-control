from migrate.versioning import api
from config import ActiveConfig
api.upgrade(ActiveConfig.SQLALCHEMY_DATABASE_URI, ActiveConfig.SQLALCHEMY_MIGRATE_REPO)
v = api.db_version(ActiveConfig.SQLALCHEMY_DATABASE_URI, ActiveConfig.SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))