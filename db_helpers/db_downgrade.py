from migrate.versioning import api
from config import ActiveConfig
v = api.db_version(ActiveConfig.SQLALCHEMY_DATABASE_URI, ActiveConfig.SQLALCHEMY_MIGRATE_REPO)
api.downgrade(ActiveConfig.SQLALCHEMY_DATABASE_URI, ActiveConfig.SQLALCHEMY_MIGRATE_REPO, v - 1)
v = api.db_version(ActiveConfig.SQLALCHEMY_DATABASE_URI, ActiveConfig.SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))