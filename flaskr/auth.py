import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST')) #tells flask to return this view when on /auth/register
def register():
    if request.method == 'POST':            #validates it as user input
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:        #makes sure it's not blank 
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(        #queries db to see if someone already has the username
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:       #if noone has that username, it adds it and the hashed password to db
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()     #need db.commit() to actually change the db
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


#login view, follows same logic as registration
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id'] #stores their id in a cookie so we know they're logged in, for other views to use
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request   #registers as function before view function 
def load_logged_in_user():
    user_id = session.get('user_id')      #grab id from session dict populated on login 

    if user_id is None:             #if theres no id to grab, theres no user 
        g.user = None
    else:                           #gets the data corresponding with that user 
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()     #remove from session so load_logged_in_user won't find them anymore
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):     #wraps views in a simple view to check if there's a logged in user
        if g.user is None:          #set in load_logged_in_user
            return redirect(url_for('auth.login'))  #redirects to the login page
                                                    #name of a view is the endpoint, prepends blueprint and adds args to end 
        return view(**kwargs)

    return wrapped_view