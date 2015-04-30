from flask.ext.wtf import Form
from werkzeug.security import check_password_hash
from wtforms import validators, PasswordField
from wtforms.ext.sqlalchemy.orm import model_form

from application import models


class BaseForm(Form):
    """
    Base class for forms.
    """

    def __init__(self, *args, **kwargs):
        field_order = getattr(self, 'field_order', None)

        # re-order the fields in the order specified
        if field_order:
            temp_fields = []

            for name in field_order:
                if name == '*':
                    # all fields not specified
                    temp_fields.extend([f for f in self._unbound_fields if f[0] not in field_order])
                else:
                    # all fields specified
                    temp_fields.append([f for f in self._unbound_fields if f[0] == name][0])
            self._unbound_fields = temp_fields
        super(BaseForm, self).__init__(*args, **kwargs)


class LoginForm(model_form(models.User,
                           base_class=BaseForm,
                           exclude=['first_name', 'last_name'],
                           field_args=models.User.get_field_args_login())):
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
        return models.User.query.filter_by(username=self.username.data).first()


class UserEditForm(model_form(models.User,
                              base_class=BaseForm,
                              field_args=models.User.get_field_args(True))):
    """
    Class representing the form handling the user editing from the admin area.
    """

    confirm = PasswordField('Repeat Password')
    field_order = ('first_name', 'last_name', 'username', 'password', 'confirm', '*')

    def __init__(self, obj=None, *args, **kwargs):

        self.id = obj.id if obj else None

        super(UserEditForm, self).__init__(obj=obj, *args, **kwargs)

    def get_user(self):
        return models.User.query.filter_by(username=self.username.data).first()

    def validate_username(self, field):
        del field

        user = self.get_user()
        if user is None:
            return

        # if not true, username was changed
        if not (self.id and user.username == models.User.query.get(self.id).username):
            raise validators.ValidationError('Username already exists.')


class UserCreateForm(model_form(models.User,
                                base_class=UserEditForm,
                                field_args=models.User.get_field_args())):
    """
    Class representing the form handling the user creating from the admin area.
    """
