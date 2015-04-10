from migrate.versioning import api
from config import ActiveConfig
from application import db
import os.path

db.create_all()
if not os.path.exists(ActiveConfig.SQLALCHEMY_MIGRATE_REPO):
    api.create(ActiveConfig.SQLALCHEMY_MIGRATE_REPO, 'db_repository')
    api.version_control(ActiveConfig.SQLALCHEMY_DATABASE_URI,
                        ActiveConfig.SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(ActiveConfig.SQLALCHEMY_DATABASE_URI,
                        ActiveConfig.SQLALCHEMY_MIGRATE_REPO,
                        api.version(ActiveConfig.SQLALCHEMY_MIGRATE_REPO))