from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, images'    #grabs posts from SQL
        ' FROM post p JOIN user u ON p.author_id = u.id'    #grabs user data from user data table and joins it with post data
        ' ORDER BY created DESC'    #sorts by most recent
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        images = request.form['Link']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, images)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], images)
            )
            
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, images'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        images = request.form['Link']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, images = ?'
                ' WHERE id = ?',
                (title, body, images, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/addimage', methods=('POST', 'GET'))
@login_required
def addimage(id):
    post = get_post(id)
    
    if request.method == 'POST': 
        image_link = request.form['Link']
        error=None 
        if not image_link:
            error = 'Link is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET images = ?'
                ' WHERE id = ?',
                (image_link, id)
            )

            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/addimage.html', post=post)


@bp.route('/<int:id>/comments', methods=('GET', 'POST'))
def comments(id):
    db = get_db()
#    comments = db.execute(
#        'SELECT comment_id, comment_body, comment_author_id'    #grabs posts from SQL
#        ' FROM comment c JOIN user u ON c.comment_author_id = u.id'    #grabs user data from user data table and joins it with post data
#        ' ORDER BY created DESC'    #sorts by most recent
#    ).fetchall()
    comments = db.execute(
        'SELECT comment_id, comment_author_id, comment_body, u.username FROM comment c' 
        ' JOIN user u ON c.comment_author_id = u.id' 
        ' WHERE comment_id = ?',
        (id,)
    ).fetchall()
    return render_template('blog/comments.html', comments = comments, id=id)


@bp.route('/<int:id>/comments/create', methods = ('GET', 'POST'))
@login_required
def addcomment(id):

    if request.method == 'POST':
        commentbody = request.form['commentbody']
        error = None

        if not commentbody:
            error = "Don't forget your comment!"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (comment_id, comment_author_id, comment_body)'
                ' VALUES (?, ?, ?)',
                (id, g.user['id'], commentbody)
            )

            db.commit()
            return redirect(url_for('blog.comments', id=id))

    return render_template('blog/addcomment.html')


