from flask import flash

from application.utils import Authentication


def check_errors():
    """
    Checks if there are any application level errors.

    :return: True if there are errors.
    """

    # true when ('admin','password') is present
    if Authentication.check_authorization('admin', 'password'):
        flash('Warning: Change default login info to something unique to prevent a potential security risk.')

from . import admin_views, main_views, forms, rest_resources
