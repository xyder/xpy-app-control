from flask.ext.restful import fields

from application.utils.helper_functions import fields_dict_from_model, parser_from_model
from application import models

# create application fields
app_fields = fields_dict_from_model(models.AppItem)
app_fields_extended = app_fields.copy()
app_fields_extended['url'] = fields.String

parser = parser_from_model(models.AppItem)

from .app_list_resource import AppListResource
from .app_resource import AppResource
