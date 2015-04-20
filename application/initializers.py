from flask.ext.admin import Admin
from flask.ext.login import LoginManager
from flask.ext.restful import Api
from werkzeug.security import generate_password_hash
from application import db, views, models
from config import ActiveConfig


def init_db():
    """
    Initializes data in the database if necessary.
    """

    # will create database and tables if not exist
    db.create_all()

    # will append a default user if none exist
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
    """
    Initializes flask-login related objects.

    :param app_: The Flask instance.
    """

    login_manager = LoginManager()
    login_manager.init_app(app_)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(user_id)


def init_admin(app_):
    """
    Initializes flask-admin related objects.

    :param app_: The Flask instance.
    """

    admin = Admin(app_, ActiveConfig.APP_NAME, index_view=views.AdminMainView())

    admin.add_view(views.AdminModelView(models.AppItem, db.session, name='Applications'))
    admin.add_view(views.AdminUserModelView(models.User, db.session, name='Users'))


def init_rest(app_):
    """
    Initializes Flask-Restful related objects and server resources.

    :param app_: The Flask instance.
    """

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