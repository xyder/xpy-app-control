from wtforms.widgets import TextInput


class CustomTextWidget(TextInput):
    def __call__(self, *args, **kwargs):
        if 'autocomplete' not in kwargs:
            kwargs['autocomplete'] = 'off'
        return super(CustomTextWidget, self).__call__(*args, **kwargs)

from .application_item import AppItem
from .user import User
