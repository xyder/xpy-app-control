from flask import make_response, jsonify
from flask.ext.restful import fields
from application import auth
from application.libs.helper_functions import fields_dict_from_model, parser_from_model
from application.models import AppItem

app_fields = fields_dict_from_model(AppItem)
app_fields_extended = app_fields.copy()
app_fields_extended['url'] = fields.String

parser = parser_from_model(AppItem)


# TODO: remove hardcoded authentication details and add user management with database
@auth.get_password
def get_password(username):
    if username == 'xyder':
        return 'pass'
    return None


@auth.error_handler
def unauthorized():
    # return 403, not 401 to prevent browsers from displaying the default auth dialog
    return make_response(jsonify({'Status': 'Unauthorized access.'}), 403)