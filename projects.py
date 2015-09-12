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

def get_project_info(db, project_id, people, news, publications):
    all_people = db.execute('select * from people where project_id=? order by id desc',
                            [project_id]).fetchall()
    people_name = []
    for single_people in all_people:
        people_name.append(single_people['name'])
    people[project_id] = people_name
    news[project_id] = db.execute('select * from news where project_id=? order by id desc',
                        [project_id]).fetchall()
    publications[project_id] = db.execute('select * from publications where project_id=? order by id desc',
                        [project_id]).fetchall()

def add_project_helper(db):
    # insert into project
    db.execute('insert into projects (name, title, description) values (?, ?, ?)',
           [request.form['project_name'], request.form['project_title'], request.form['project_description']])
    db.commit()
    project_id = db.execute('select max(id) from projects').fetchall()[0]['max(id)']
    # insert into people
    for people_name in request.form.getlist('people_name'):
        db.execute('insert into people (name, project_id) values (?, ?)', [people_name, project_id])
    # insert into news
    news_title = request.form.getlist('news_title')
    news_description = request.form.getlist('news_description')
    for i in range(len(news_title)):
        db.execute('insert into news (title, description, project_id) values (?, ?, ?)', [news_title[i], 
            news_description[i], project_id])
    # insert into publications
    for description in request.form.getlist('publication_description'):
        db.execute('insert into publications (description, project_id) values (?, ?)', [description, project_id])
    db.commit()

def delete_project_helper(db, project_id):
    db.execute('delete from projects where id=?', [project_id])
    db.execute('delete from people where project_id=?', [project_id])
    db.execute('delete from publications where project_id=?', [project_id])
    db.execute('delete from news where project_id=?', [project_id])
    db.commit()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_projects():
    db = get_db()
    projects = db.execute('select * from projects order by id desc').fetchall()
    people = dict()
    news = dict()
    publications = dict()
    for project in projects:
        get_project_info(db, project['id'], people, news, publications)
    return render_template('show_projects.html', projects=projects, people=people, news=news, publications=publications)

@app.route('/add', methods=['GET','POST'])
def add_project():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        return render_template('add_project.html')
    else:
        db = get_db()
        add_project_helper(db)
        flash('New project was successfully added')
        return redirect(url_for('show_projects'))

@app.route('/delete_project/<project_id>', methods=['GET'])
def delete_project(project_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    project_id = int(project_id)
    delete_project_helper(db, project_id)
    return redirect(url_for('show_projects'))

@app.route('/update_project/<project_id>', methods=['GET', 'POST'])
def update_project(project_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    project_id = int(project_id)
    if request.method == 'GET':
        project = db.execute('select * from projects where id=?', [project_id]).fetchall()[0]
        people = dict()
        news = dict()
        publications = dict()
        get_project_info(db, project_id, people, news, publications)
        return render_template('update_project.html', project=project, people=people, news=news, publications=publications)
    else:
        delete_project_helper(db, project_id)
        add_project_helper(db)
        return redirect(url_for('show_projects'))
    
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