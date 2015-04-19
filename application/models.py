from flask.ext.login import UserMixin
from wtforms import validators
from application import db
from wtforms.widgets import TextInput, PasswordInput
from application.libs.helper_functions import get_command
from config import ActiveConfig


class User(db.Model, UserMixin):
    """
    User Model - matches an user item from the database
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, index=True)
    last_name = db.Column(db.Text, index=True)
    username = db.Column(db.Text, unique=True, index=True)
    password = db.Column(db.Text)

    def __init__(self):
        self.first_name = ''
        self.last_name = ''
        self.username = ''
        self.password = ''

    @property
    def field_args(self):
        """
        Gets the field arguments for the automatic form creation.
        """
        return {
            User.first_name.key: {'widget': TextInput(), 'label': 'First Name'},
            User.last_name.key: {'widget': TextInput(), 'label': 'Last Name'},
            User.username.key: {'widget': TextInput(), 'label': 'Username',
                                'validators': [validators.DataRequired()]},
            User.password.key: {'widget': PasswordInput(), 'label': 'Password',
                                'validators': [validators.DataRequired(),
                                               validators.EqualTo('confirm', message='Password must match.')]}
        }


class AppItem(db.Model):
    """
    AppItem Model - matches an application item from the database
    """
    __tablename__ = 'apps'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, index=True)
    description = db.Column(db.Text, index=True)
    start_file = db.Column(db.Text, index=True)
    start_args = db.Column(db.Text, index=True)
    stop_file = db.Column(db.Text, index=True)
    stop_args = db.Column(db.Text, index=True)
    compare_term = db.Column(db.Text, index=True)
    check_name = db.Column(db.Boolean, default=False)
    check_exe = db.Column(db.Boolean, default=False)
    check_cmd = db.Column(db.Boolean, default=False)
    start_in_command_prompt = db.Column(db.Boolean, default=False)
    stop_in_command_prompt = db.Column(db.Boolean, default=False)

    def __init__(self):
        self.name = ''
        self.description = ''
        self.start_file = ''
        self.start_args = ''
        self.stop_file = ''
        self.stop_args = ''
        self.compare_term = ''
        self.check_name = False
        self.check_exe = False
        self.check_cmd = False
        self.start_in_command_prompt = False
        self.stop_in_command_prompt = False

    @property
    def field_args(self):
        """
        Gets the field arguments for the automatic form creation.
        """
        return {
            AppItem.name.key: {'widget': TextInput(), 'label': 'Entry Name'},
            AppItem.start_file.key: {'widget': TextInput(), 'label': 'Start Command Path'},
            AppItem.start_args.key: {'widget': TextInput(), 'label': 'Start Command Args'},
            AppItem.stop_file.key: {'widget': TextInput(),
                                    'label': 'Stop Command (Stop All - only; leave empty for default end task)'},
            AppItem.stop_args.key: {'widget': TextInput(),
                                    'label': 'Stop Command Args (Stop All - only; leave empty for default end task)'},
            AppItem.compare_term.key: {'widget': TextInput(), 'label': 'Comparison term'},
            AppItem.start_in_command_prompt.key: {'label': 'Start in command prompt'},
            AppItem.stop_in_command_prompt.key: {'label': 'Stop in command prompt'},
            AppItem.check_exe.key: {'label': 'Compare term with executable path'},
            AppItem.check_cmd.key: {'label': 'Compare term with command line (executable path and args)'},
            AppItem.check_name.key: {'label': 'Compare term with image name (usually the executable file name)'}
        }

    @property
    def url(self):
        return 'http://' + ActiveConfig.SERVER_NAME\
               + ActiveConfig.REST_URL_APPS\
               + '/' + ('' if self.id is None else str(self.id))

    def get_start_command(self):
        """
        Gets the associated start command.
        """
        return get_command(self.start_file, self.start_args, self.start_in_command_prompt)

    def get_stop_command(self):
        """
        Gets the asociated stop command.
        """
        return get_command(self.stop_file, self.stop_args, self.stop_in_command_prompt)

    def compare_process(self, proc):
        """
        Determines if a specified process is validated using the comparison term and type

        :return: True if it matches.
        """
        if self.check_cmd and proc['CommandLine'] and proc['CommandLine'] == self.compare_term:
            return True
        if self.check_name and proc['Name'] and proc['Name'] == self.compare_term:
            return True
        if self.check_exe and proc['ExecutablePath'] and proc['ExecutablePath'] == self.compare_term:
            return True

    def __repr__(self):
        """
        Gets the string representation of the application item.
        """
        return '[Id = {0}, Name = {1}]'.format(self.id, self.name)