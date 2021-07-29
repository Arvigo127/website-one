import sqlite3

import click       #command line stuff 
from flask import current_app, g    #g is special object for request data that might be accessed, connection is reused
from flask.cli import with_appcontext


def get_db():           #this will connect to SQL db when request is made and close connection 
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None) #populates db in g with None if theres nothing there

    if db is not None:  #closes db if theres something in it 
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')       #makes a command line command to do this function 
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command("mycommand")
def command_line_command():
    click.echo("YOU called me")
    

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(command_line_command)

    