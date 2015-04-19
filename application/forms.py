from flask.ext.wtf import Form
from werkzeug.security import check_password_hash
from wtforms import fields, validators
from application.models import User


class LoginForm(Form):

    username = fields.StringField(validators=[validators.DataRequired()])
    password = fields.PasswordField(validators=[validators.DataRequired()])

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