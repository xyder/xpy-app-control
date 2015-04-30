from flask import request, redirect, url_for
from flask.ext.admin import expose, AdminIndexView, helpers
from flask.ext.admin.contrib.sqla import ModelView
import flask.ext.login as login
from werkzeug.security import generate_password_hash

from . import forms, check_errors


class AdminMainView(AdminIndexView):

    @expose('/')
    def index(self):

        # prevent unauthorized access
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view', next=request.url))

        check_errors()
        return super(AdminMainView, self).index()

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        req_form = forms.LoginForm(request.form)
        if helpers.validate_form_on_submit(req_form):
            user = req_form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(request.args.get('next') or '/admin')

        check_errors()

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
        return forms.UserCreateForm()

    def edit_form(self, obj=None):
        return forms.UserEditForm(obj=obj)

    def create_model(self, form):
        form.password.data = generate_password_hash(form.password.data)
        return super(AdminUserModelView, self).create_model(form)

    def update_model(self, form, model):
        form.password.data = generate_password_hash(form.password.data)
        return super(AdminUserModelView, self).update_model(form, model)
