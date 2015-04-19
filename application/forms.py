from flask.ext.wtf import Form
from werkzeug.security import check_password_hash
from wtforms import validators, PasswordField
from wtforms.ext.sqlalchemy.orm import model_form
from application.models import User


class LoginForm(model_form(User, base_class=Form, exclude=['first_name', 'last_name'],
                           field_args=User.get_field_args_login())):

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


class UserCreateForm(model_form(User, base_class=Form, field_args=User.get_field_args_create())):
    confirm = PasswordField('Repeat Password')

    def validate_username(self, field):
        del field

        user = self.get_user()
        if user is not None:
            raise validators.ValidationError('Username already exists.')

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()