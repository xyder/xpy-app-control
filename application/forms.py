from flask.ext.wtf import Form
from werkzeug.security import check_password_hash
from wtforms import validators, PasswordField
from wtforms.ext.sqlalchemy.orm import model_form
from application.models import User


class LoginForm(model_form(User, base_class=Form, exclude=['first_name', 'last_name'],
                           field_args=User.get_field_args_login())):
    """
    Class representing the form handling authentication in the admin area.
    """

    def validate_username(self, field):
        del field

        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Username does not exist.')

    def validate_password(self, field):
        del field

        user = self.get_user()
        if user is None:
            return

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Password is invalid.')

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()


class UserEditForm(model_form(User, base_class=Form, field_args=User.get_field_args(True))):
    """
    Class representing the form handling the user editing from the admin area.
    """

    confirm = PasswordField('Repeat Password')

    def __init__(self, obj=None, *args, **kwargs):

        self.id = obj.id if obj else None

        super(UserEditForm, self).__init__(obj=obj, *args, **kwargs)

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()

    def validate_username(self, field):
        del field

        user = self.get_user()
        if user is None:
            return

        # if not true, username was changed
        if not (self.id and user.username == User.query.get(self.id).username):
            raise validators.ValidationError('Username already exists.')


class UserCreateForm(model_form(User, base_class=UserEditForm, field_args=User.get_field_args())):
    """
    Class representing the form handling the user creating from the admin area.
    """

    # repeating this places the confirm field after the form
    confirm = PasswordField('Repeat Password')
