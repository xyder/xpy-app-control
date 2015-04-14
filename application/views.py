from flask import render_template, request, jsonify
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

from application import app, db, auth, mapper
from .models import AppItem


@app.route('/')
def index():
    """
    Generates the main page and the automatic form using a generic AppItem object

    :return: the template to be served to the client
    """
    params = {'title': 'Main'}
    app_item = AppItem()
    # crates a model class from the application item
    app_item_form = model_form(AppItem, db.session, base_class=Form, field_args=app_item.field_args)
    return render_template('index.html', params=params, form=app_item_form(obj=app_item))


@app.route('/rpc', methods=['POST'])
@auth.login_required
def rpc():
    # Request format: {"jsonrpc": "2.0", "method": methodname, "params": params, "id": 1}

    # providing a safe failure in case the json is None
    json_obj = {"jsonrpc": "2.0", "method": None, "id": 0}

    if request.json is not None:
        json_obj = request.json

        # override to prevent needless verbosity
        json_obj['jsonrpc'] = json_obj['jsonrpc'] if 'jsonrpc' in json_obj else '2.0'
    data = mapper(json_obj)
    return jsonify(data)