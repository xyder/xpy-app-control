from flask import render_template
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

from application import app, db
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
