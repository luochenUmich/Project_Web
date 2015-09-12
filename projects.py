from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='/tmp/projects.db',
    DEBUG=True,
    SECRET_KEY='SECRET',
    USERNAME='admin',
    PASSWORD='default'
))


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_projects():
    db = get_db()
    projects = db.execute('select * from projects order by id desc').fetchall()
    for project in projects:
        all_people = db.execute('select * from people where project_id=? order by id desc',
                            [project['id']]).fetchall()
        people_name = []
        for single_people in all_people:
            people_name.append(single_people['name'])
        people = dict()
        people[project['id']] = people_name
        news = dict()
        news[project['id']] = db.execute('select * from news where project_id=? order by id desc',
                            [project['id']]).fetchall()
        publications = dict()
        publications[project['id']] = db.execute('select * from publications where project_id=? order by id desc',
                            [project['id']]).fetchall()
    return render_template('show_projects.html', projects=projects, people=people, news=news, publications=publications)


# Todo figure out how to deal with multiple add
@app.route('/add', methods=['GET','POST'])
def add_project():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        return render_template('add_project.html')
    else:
        db = get_db()
        # db.execute('insert into entries (title, text) values (?, ?)',
        #            [request.form['title'], request.form['text']])
        db.commit()
        flash('New project was successfully posted')
        return redirect(url_for('show_projects'))

# @app.route('/add_people', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_db()
#     db.execute('insert into entries (title, text) values (?, ?)',
#                [request.form['title'], request.form['text']])
#     db.commit()
#     flash('New project was successfully posted')
#     return redirect(url_for('show_projects'))

# @app.route('/add_news', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_db()
#     db.execute('insert into entries (title, text) values (?, ?)',
#                [request.form['title'], request.form['text']])
#     db.commit()
#     flash('New project was successfully posted')
#     return redirect(url_for('show_projects'))

# @app.route('/add_publication', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_db()
#     db.execute('insert into entries (title, text) values (?, ?)',
#                [request.form['title'], request.form['text']])
#     db.commit()
#     flash('New project was successfully posted')
#     return redirect(url_for('show_projects'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_projects'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_projects'))

if __name__ == '__main__':
    app.run()