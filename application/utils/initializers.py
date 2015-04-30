from flask.ext.admin import Admin
from flask.ext.login import LoginManager
from flask.ext.restful import Api

from application import views, models
from application.utils import RPCServer
from application.utils.helper_functions import register_class_to_rpc
from config import ActiveConfig


def init_db(db):
    """
    Initializes data in the database if necessary.
    """

    # will create database and tables if not exist
    db.create_all()

    # will append a default user if none exist
    if models.User.query.count() == 0:
        default_user = models.User('admin', 'password', 'John', 'Smith')
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


def init_admin(app, db):
    """
    Initializes flask-admin related objects.

    :param app: The Flask instance.
    """

    admin = Admin(app, ActiveConfig.APP_NAME, index_view=views.admin_views.AdminMainView())

    # register admin views
    admin.add_view(views.admin_views.AdminModelView(models.AppItem, db.session, name='Applications'))
    admin.add_view(views.admin_views.AdminUserModelView(models.User, db.session, name='Users'))


def init_rest(app_):
    """
    Initializes Flask-Restful related objects and server resources.

    :param app_: The Flask instance.
    """

    rest_api = Api(app_)
    rest_api.add_resource(views.rest_resources.AppListResource,
                          ActiveConfig.REST_URL_APPS_LIST,
                          ActiveConfig.REST_URL_APPS_LIST + '/')
    rest_api.add_resource(views.rest_resources.AppResource,
                          ActiveConfig.REST_URL_APPS_ITEM,
                          ActiveConfig.REST_URL_APPS,
                          ActiveConfig.REST_URL_APPS + '/')


def init_rpc(mapper):
    register_class_to_rpc(RPCServer, mapper)
