from flask import render_template, request, jsonify, url_for, redirect, flash, make_response
from flask.ext.admin import AdminIndexView, expose, helpers
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.wtf import Form
import flask.ext.login as login
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.ext.sqlalchemy.orm import model_form

from application import app, db, mapper
from application.forms import LoginForm, UserCreateForm, UserEditForm
from config import ActiveConfig
from .models import AppItem, User


def check_errors():
    """
    Checks if there are any application level errors.

    :return: True if there are errors.
    """
    user = User.query.filter_by(username='admin').first()
    # true when user exists and password is set to default
    if user is not None and check_password_hash(user.password, 'password'):
        flash('Warning: Change default login info to something unique to prevent a potential security risk.')


class AdminMainView(AdminIndexView):

    @expose('/')
    def index(self):
        check_errors()
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view', next=request.url))
        return super(AdminMainView, self).index()

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        req_form = LoginForm(request.form)
        if helpers.validate_form_on_submit(req_form):
            user = req_form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(request.args.get('next') or '/')

        self._template_args['form'] = req_form
        return super(AdminMainView, self).index()

    @expose('/logout')
    def logout_view(self):
        login.logout_user()
        return redirect(request.args.get('next') or '/')


class AdminModelView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def _handle_view(self, name, **kwargs):
        check_errors()
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))


class AdminUserModelView(AdminModelView):

    # set the passwords to be masked
    column_formatters = dict(password=lambda v, c, m, p: '* * * * *')

    def create_form(self, obj=None):
        return UserCreateForm()

    def edit_form(self, obj=None):
        return UserEditForm(obj=obj)

    def create_model(self, form):
        form.password.data = generate_password_hash(form.password.data)
        return super(AdminUserModelView, self).create_model(form)

    def update_model(self, form, model):
        form.password.data = generate_password_hash(form.password.data)
        return super(AdminUserModelView, self).update_model(form, model)


# application endpoints

@app.route('/')
def index():
    """
    Generates the main page and the automatic form using a generic AppItem object

    :return: the template to be served to the client
    """

    check_errors()

    params = {'title': 'Main'}
    app_item = AppItem()
    # crates a model class from the application item
    app_item_form = model_form(AppItem, db.session, base_class=Form, field_args=app_item.field_args)
    return render_template('index.html', params=params, form=app_item_form(obj=app_item), app_config=ActiveConfig)


@app.route('/rpc', methods=['POST'])
def rpc():
    if not login.current_user.is_authenticated():
        # return 403, not 401 to prevent browsers from displaying the default auth dialog
        return make_response(jsonify({'Status': 'Unauthorized access.'}), 403)

    # Request format: {"jsonrpc": "2.0", "method": methodname, "params": params, "id": 1}

    # providing a safe failure in case the json is None
    json_obj = {"jsonrpc": "2.0", "method": None, "id": 0}

    if request.json is not None:
        json_obj = request.json

        # override to prevent needless verbosity
        json_obj['jsonrpc'] = json_obj['jsonrpc'] if 'jsonrpc' in json_obj else '2.0'
    data = mapper(json_obj)
    return jsonify(data)