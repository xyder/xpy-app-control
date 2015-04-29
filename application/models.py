from werkzeug.security import generate_password_hash
from wtforms import validators
from application import db
from wtforms.widgets import TextInput, PasswordInput
from application.libs.helper_functions import get_command
from config import ActiveConfig


class CustomTextWidget(TextInput):
    def __call__(self, *args, **kwargs):
        if 'autocomplete' not in kwargs:
            kwargs['autocomplete'] = 'off'
        return super(CustomTextWidget, self).__call__(*args, **kwargs)


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
        return 'http://' + ActiveConfig.SERVER_NAME \
               + ActiveConfig.REST_URL_APPS \
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