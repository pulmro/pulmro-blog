from functools import wraps
from blog import loginmanager
from flask_login import current_user


def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return loginmanager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
