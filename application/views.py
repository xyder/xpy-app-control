from flask import render_template, request, jsonify, url_for, redirect, flash, make_response
from flask.ext.admin import AdminIndexView, expose, helpers
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.wtf import Form
import flask.ext.login as login
from werkzeug.security import generate_password_hash
from wtforms.ext.sqlalchemy.orm import model_form

from application import app, db, mapper
from application.authentication import Authentication
from application.forms import LoginForm, UserCreateForm, UserEditForm
from config import ActiveConfig
from .models import AppItem


def check_errors():
    """
    Checks if there are any application level errors.

    :return: True if there are errors.
    """

    # true when ('admin','password') is present
    if Authentication.check_authorization('admin', 'password'):
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

@app.route('/', methods=['GET', 'POST'])
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

    login_form = LoginForm(request.form)
    if helpers.validate_form_on_submit(login_form):
        user = login_form.get_user()
        login.login_user(user)
        params['retry_login'] = False
    else:
        if login_form.errors:
            params['retry_login'] = True

    return render_template('index.html',
                           params=params,
                           form=app_item_form(obj=app_item),
                           login_form=login_form,
                           app_config=ActiveConfig)


@app.route('/rpc', methods=['POST'])
@Authentication.login_required
def rpc():
    """
    Endpoint for the RPC requests server.

    :return: The generated response in JSON format.
    """

    # check if json data was sent
    if request.json is None:
        return make_response(jsonify({'Status': 'No data received.'}), 400)

    # check if all necessary fields are present
    required_fields = ['id', 'method']
    for field in required_fields:
        if field not in request.json:
            return make_response(jsonify({'Status': 'Field <' + field + '> not specified.'}), 400)

    # Request format: {
    #       ["jsonrpc": "2.0",]
    #       ["username": "username",]
    #       ["password": "password",]
    #       "method": methodname,
    #       ["params": params,]
    #       "id": 1
    # }

    # override to prevent needless verbosity
    request.json['jsonrpc'] = request.json['jsonrpc'] if 'jsonrpc' in request.json else '2.0'

    ret_data = mapper(request.json)
    code = 200
    if 'result' in ret_data and 'code' in ret_data['result']:
        code = ret_data['result']['code']

    return make_response(jsonify(ret_data), code)
