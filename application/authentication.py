from functools import wraps
from flask import request, make_response, jsonify
import flask.ext.login as login
from werkzeug.security import check_password_hash
from application.models import User


class Authentication:
    """
    Class that contains methods for authentication and user validation.
    """

    @staticmethod
    def check_authorization(username, password):
        """
        checks if the username/password pair is valid.

        :return: True if valid.
        """

        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password):
            return False
        return True

    @staticmethod
    def check_authorization_dict(dict_obj):
        """
        Checks if the object contains the 'username' and 'password' fields and validates the pair.

        :return: True if present and valid.
        """

        if dict_obj is None or 'username' not in dict_obj or 'password' not in dict_obj:
            return False
        return Authentication.check_authorization(dict_obj['username'], dict_obj['password'])

    @staticmethod
    def login_required(f):
        """
        Decorator that checks if a request contains valid authorization data either in the header or the json object.
        """

        @wraps(f)
        def decorated(*args, **kwargs):
            # We need to ignore authentication headers for OPTIONS to avoid
            # unwanted interactions with CORS.
            # Chrome and Firefox issue a preflight OPTIONS request to check
            # Access-Control-* headers, and will fail if it returns 401.
            if request.method != 'OPTIONS':
                if not (login.current_user.is_authenticated()
                        or Authentication.check_authorization_dict(request.authorization)
                        or Authentication.check_authorization_dict(request.json)):
                    # return 403, not 401 to prevent browsers from displaying the default auth dialog
                    return make_response(jsonify({'Status': 'Unauthorized access.'}), 403)
            return f(*args, **kwargs)
        return decorated