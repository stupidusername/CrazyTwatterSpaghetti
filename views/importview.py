from flask import redirect, url_for
from flask_admin import BaseView, expose
from forms.importform import ImportForm


class ImportView(BaseView):
    """
    Import CSV view class.
    """

    @expose(url='/', methods=('GET', 'POST'))
    def index(self):
        form = ImportForm()
        if form.validate_on_submit():
            result = form.save()
            return redirect(url_for('account.index_view'))
        return self.render('import.html', form=form)
