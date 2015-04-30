from flask import render_template, request, jsonify, redirect, make_response
from flask.ext.admin import helpers
from flask.ext.wtf import Form
import flask.ext.login as login
from wtforms.ext.sqlalchemy.orm import model_form

from application import app, db, mapper, models
from application.utils import Authentication
from config import ActiveConfig
from . import forms, check_errors


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Generates the main page and the automatic form using a generic AppItem object

    :return: the template to be served to the client
    """

    params = {'title': 'Main'}
    app_item = models.AppItem()
    # crates a model class from the application item
    app_item_form = model_form(models.AppItem, db.session, base_class=Form, field_args=app_item.field_args)

    login_form = forms.LoginForm(request.form)
    if helpers.validate_form_on_submit(login_form):
        user = login_form.get_user()
        login.login_user(user)
        params['retry_login'] = False

        # redirect to prevent form double submit
        return redirect(request.url)
    else:
        if login_form.errors:
            params['retry_login'] = True

    params['is_authenticated'] = login.current_user.is_authenticated()

    check_errors()

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
