from flask.ext.admin import Admin
from flask.ext.login import LoginManager
from flask.ext.restful import Api
from werkzeug.security import generate_password_hash
from application import db, views, models
from config import ActiveConfig

# initialize database if necessary
def init_db():
    # will create database and tables if not exist
    db.create_all()

    # will append a default user if none exist
    # TODO: flash warning message about the existence of a potential security risk.
    if models.User.query.count() == 0:
        default_user = models.User()

        default_user.username = 'admin'
        default_user.password = generate_password_hash('password')
        default_user.first_name = 'John'
        default_user.last_name = 'Smith'

        db.session.add(default_user)
        db.session.commit()


# initialize flask login
def init_login(app_):
    login_manager = LoginManager()
    login_manager.init_app(app_)

    # create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(user_id)


# initalize flask admin
def init_admin(app_):
    admin = Admin(app_, ActiveConfig.APP_NAME, index_view=views.AdminMainView())

    admin.add_view(views.AdminModelView(models.AppItem, db.session, name='Applications'))
    admin.add_view(views.AdminModelView(models.User, db.session, name='Users'))


# initialize rest interface
def init_rest(app_):
    from application.resources.app_resource import AppResource
    from application.resources.app_list_resource import AppListResource

    rest_api = Api(app_)
    rest_api.add_resource(AppListResource,
                          ActiveConfig.REST_URL_APPS_LIST,
                          ActiveConfig.REST_URL_APPS_LIST + '/')
    rest_api.add_resource(AppResource,
                          ActiveConfig.REST_URL_APPS_ITEM,
                          ActiveConfig.REST_URL_APPS,
                          ActiveConfig.REST_URL_APPS + '/')