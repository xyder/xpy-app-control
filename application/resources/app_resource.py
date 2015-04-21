from flask.ext.restful import Resource, abort, marshal_with
from application import db
from application.authentication import Authentication
from application.libs.helper_functions import str_to_bool
from application.models import AppItem
from application.resources import app_fields, app_fields_extended, parser


class AppResource(Resource):
    """
    Resource class that processes requests for GET, DELETE, PUT and POST for an application item.
    """

    @staticmethod
    def parse_args_to_app(app_item, parsed_args):
        """
        Fills an application item with the given values.

        :param app_item: a new application item or a previously existing one.

        :param parsed_args: dictionary containing the new values to be added/edited

        :return: the newly edited application item.
        """
        for field in app_fields:
            # exclude the id from modifiable values. it is read-only and automatically generated.
            if field != 'id':
                # exclude values that were not specified by the request
                if parsed_args[field] is not None:
                    # process boolean values separately
                    if type(getattr(app_item, field)) == bool:
                        setattr(app_item, field, str_to_bool(parsed_args[field]))
                    else:
                        setattr(app_item, field, parsed_args[field])
        return app_item

    @marshal_with(app_fields_extended)
    def get(self, id_app=''):
        """
        Endpoint that responds to a GET request with a specified application item.

        :param id_app: can be an id corresponding to a registered application item or 'default'

        :return: The specified application item.
        """
        if id_app == 'default' or id_app == '':
            return AppItem()
        app_item = AppItem.query.get(id_app)
        if not app_item:
            abort(404, message="App {} doesn't exist.".format(id_app))
        return app_item

    @staticmethod
    @Authentication.login_required
    def delete(id_app):
        """
        Endpoit that responds to a DELETE request and removes a specified application item from the
        database.

        :param id_app: The id of the specified application item.
        """
        app_item = AppItem.query.get(id_app)
        if not app_item:
            abort(404, message="App {} doesn't exist.".format(id_app))
        db.session.delete(app_item)
        db.session.commit()
        return {}, 204

    @Authentication.login_required
    @marshal_with(app_fields)
    def put(self, id_app):
        """
        Endpoint that updates the database information for the specified application item.
        :param id_app: The id of the specified application item.
        """
        # fetch the application item from the database
        app_item = AppItem.query.get(id_app)
        if not app_item:
            abort(404, message="App {} doesn't exist.".format(id_app))

        # update the application item with the given arguments
        app_item = AppResource.parse_args_to_app(app_item, parser.parse_args())
        db.session.add(app_item)
        db.session.commit()
        return app_item, 201

    @Authentication.login_required
    @marshal_with(app_fields)
    def post(self, id_app=''):
        """
        Endpoint that adds a new application item.
        :param id_app: Can only be 'add' to restrict the viable URL path.
        :return:
        """
        if id_app != 'add' and id_app != '':
            abort(404, message='Command {} not allowed.'.format(id_app))

        # fill the application item with the given arguments
        app_item = AppResource.parse_args_to_app(AppItem(), parser.parse_args())
        db.session.add(app_item)
        db.session.commit()
        return app_item, 201