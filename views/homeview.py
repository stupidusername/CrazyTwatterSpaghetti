from flask import redirect, url_for
from flask_admin import AdminIndexView, expose


class HomeView(AdminIndexView):
    """
    View class for admin panel index.
    """

    @expose('/')
    def index(self):
        return redirect(url_for('account.index_view'))
