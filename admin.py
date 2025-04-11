from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField
from flask import url_for, redirect, request, abort
from flask_login import current_user
from functools import wraps

from extensions import db
from models import User, Post, Follow


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login_page', next=request.url))


class UserView(SecureModelView):
    column_list = ('id', 'username', 'email', 'created_at', 'profile_picture')
    column_searchable_list = ('username', 'email')
    column_filters = ('created_at', 'gender')
    column_exclude_list = ('password_hash',)
    form_excluded_columns = ('password_hash', 'posts', 'likes', 'comments')
    can_create = True
    can_edit = True
    can_delete = True
    form_extra_fields = {
        'profile_picture': FileUploadField('Profile Picture',base_path='public/uploads/profile_pics')
    }


class PostView(SecureModelView):
    column_list = ('id', 'author', 'caption', 'created_at', 'image_url', 'hidden_tag')
    column_searchable_list = ('caption',)
    column_filters = ('created_at', 'hidden_tag')
    can_create = True
    can_edit = True
    can_delete = True
    form_extra_fields = {
        'image_url': FileUploadField('Image', base_path='public/uploads/posts')
    }


class FollowsView(SecureModelView):
    column_list = ('id', 'follower_id', 'followed_id', 'created_at')
    column_searchable_list = ('follower_id', 'followed_id')
    column_filters = ('created_at',)
    can_create = True
    can_edit = True
    can_delete = True


def init_admin(app):
    admin = Admin(app,
                  index_view=AdminIndexView(
                      name='Valenstagram Admin',
                      template='admin/index.html',
                      url='/admin/home'
                    ),
                  template_mode='bootstrap4',
                  )
    admin.add_view(UserView(User, db.session, name='Utilisateurs'))
    admin.add_view(PostView(Post, db.session, name='Publications'))
    admin.add_view(FollowsView(Follow, db.session, name='Abonnements'))
    return admin