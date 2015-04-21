from flask.ext.restful import fields
from application.libs.helper_functions import fields_dict_from_model, parser_from_model
from application.models import AppItem

app_fields = fields_dict_from_model(AppItem)
app_fields_extended = app_fields.copy()
app_fields_extended['url'] = fields.String

parser = parser_from_model(AppItem)
