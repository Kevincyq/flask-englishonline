from flask import (
     Blueprint, flash, redirect, render_template, request, url_for, current_app
)

from werkzeug.exceptions import abort

from flaskr import db
from .auth import login_required
from .models import Blog
from flask_login import current_user
from datetime import datetime


bp = Blueprint('blog', __name__, url_prefix='/blog')



@bp.route('/blog', methods = ('GET',))
def query():
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.paginate(page, current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    next_url = url_for('blog.query', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('blog.query', page=pagination.prev_num) \
        if pagination.has_prev else None

    return render_template('blog/blog.html', pagination=pagination, posts=posts, next_url=next_url, prev_url=prev_url)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        author_id = current_user.id
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post = Blog(title, body, author_id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('blog.query'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = Blog.query.filter_by(id=id).first()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post.author_id != current_user.id:
        abort(403)
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post = Blog.query.filter_by(id=id).first()
            post.title = title
            post.body = body
            post.created = datetime.now()
            db.session.commit()
            return redirect(url_for('blog.query'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.query'))