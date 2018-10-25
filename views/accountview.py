from flask_admin import expose
from flask_admin.contrib.sqla import ModelView


class AccountView(ModelView):
    """
    Model view class for account model.
    """

    # Remove fields from the create and edit forms.
    form_excluded_columns = ['status', 'status_updated_at', 'cookies']

    # Define formatters.
    column_formatters = {
        'cookies': lambda view, ctx, model, name: bool(model.cookies)
    }
