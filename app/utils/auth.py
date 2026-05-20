"""Authentication helpers for admin routes."""

from functools import wraps

from flask import abort, jsonify, redirect, request, url_for
from flask_login import current_user


def admin_required(view):
    """Require a logged-in AdminUser (HTML redirect or JSON 403)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        from app.models import AdminUser

        if not current_user.is_authenticated:
            if request.is_json or request.accept_mimetypes.best == 'application/json':
                return jsonify({'success': False, 'error': 'Admin login required'}), 401
            return redirect(url_for('main.admin_login', next=request.url))

        if not isinstance(current_user, AdminUser):
            if request.is_json or request.accept_mimetypes.best == 'application/json':
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
            return redirect(url_for('main.admin_login'))

        return view(*args, **kwargs)

    return wrapped
