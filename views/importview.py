from flask_admin import BaseView, expose


class ImportView(BaseView):
    """
    Import CSV view class.
    """

    @expose(url='/', methods=('GET', 'POST'))
    def index(self):
        return ':D'
