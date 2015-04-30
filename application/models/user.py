from werkzeug.security import generate_password_hash
from wtforms import validators
from wtforms.widgets import PasswordInput

from application import db
from . import CustomTextWidget


class User(db.Model):
    """
    User Model - matches an user item from the database
    """

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, index=True)
    last_name = db.Column(db.Text, index=True)
    username = db.Column(db.Text, unique=True, index=True)
    password = db.Column(db.Text)

    def __init__(self, username='', password='', first_name='', last_name=''):
        # force defaults in case None is sent
        self.first_name = first_name or ''
        self.last_name = last_name or ''
        self.username = username or ''
        self.password = generate_password_hash(password or '')

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    @staticmethod
    def get_field_args_login():
        """
        Gets the field arguments for the automatic form creation.
        """

        return {
            User.username.key: {'widget': CustomTextWidget(), 'label': 'Username',
                                'validators': [validators.DataRequired()]},
            User.password.key: {'widget': PasswordInput(), 'label': 'Password',
                                'validators': [validators.DataRequired()]}
        }

    @staticmethod
    def get_field_args(is_editing=False):
        """
        Gets the field arguments for the automatic form creation.
        """

        fields = User.get_field_args_login()
        fields[User.first_name.key] = {'widget': CustomTextWidget(), 'label': 'First Name'}
        fields[User.last_name.key] = {'widget': CustomTextWidget(), 'label': 'Last Name'}

        match_validator = validators.EqualTo('confirm', message='Password must match.')
        if is_editing:
            fields[User.password.key]['validators'] = [validators.Optional(), match_validator]
        else:
            fields[User.password.key]['validators'].append(match_validator)

        return fields

    @property
    def get_full_name(self):
        if self.first_name:
            if self.last_name:
                return self.first_name + ' ' + self.last_name
            else:
                return self.first_name
        else:
            return self.last_name or self.username

    def __repr__(self):
        return self.get_full_name
