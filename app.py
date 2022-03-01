# SWIFT Taskbook
# Web Application for Task Management

# flask web objects
from auth import auth
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, session, flash
from werkzeug.exceptions import HTTPException,BadRequest,NotFound,InternalServerError
from datetime import date
import dataset

taskbook_db = dataset.connect('sqlite:///taskbook.db')
today = date.today()
# the base Flask object
app = Flask(__name__)
# for cookies and sesion encryption
app.config['SECRET_KEY'] = 'walsh-swe'

# ---------------------------
# web application routes
# ---------------------------

# Home/Default Route
@app.get('/')
@app.get('/home')
def homepage():
    if session.get('user_authenticated'):
        cust_db = taskbook_db.get_table('customization')
        try:
            cust_table = cust_db.find_one(email=session['user_email'])
            default_view = cust_table['view']
            return render_template(default_view + ".html")
        except Exception as e:
            # No current View is set or view is stored incorrectly
            return dashboard();
    return render_template("homepage.html")

# Dashboard Route
@app.get('/dashboard')
def dashboard():
    if session.get('user_authenticated'):
        return render_template("dashboard.html", user=session['user_email'])
    flash('You need to be logged in first', category='error')
    return redirect(url_for('auth.login'))

# Settings route
@app.get('/settings')
def settings():
    if session.get('user_authenticated'):
        return render_template("settings.html", user=session['user_email'])
    flash('You need to be logged in first', category='error')
    return redirect(url_for('auth.login'))

# About route
@app.get('/about')
def about():
    return render_template("about.html")

# Calendar Route
@app.get('/calendar')
def calendar():
    if session.get('user_authenticated'):
        return render_template("calendar.html", user=session['user_email'])
    flash('You need to be logged in first', category='error')
    return redirect(url_for('auth.login'))

# Task View Route
@app.get('/tasks')
@app.get('/tasks/<int:year>-<int:month>-<int:day>')
def tasks(year=today.year, month=today.month, day=today.day):
    if session.get('user_authenticated'):
        #this check is so they don't put completely ludicrous dates in.
        if(month > 12 or day > 31 or year < 1800):
            return redirect(url_for('tasks'))
        return render_template("tasks.html", user=session['user_email'], year=year, month=month, day=day)
    flash('You need to be logged in first', category='error')
    return redirect(url_for('auth.login'))

# Weekly Route
@app.get('/weekly')
def weekly():
    if session.get('user_authenticated'):
        return render_template("weekly.html", user=session['user_email'])
    flash('You need to be logged in first', category='error')
    return redirect(url_for('auth.login'))

#--------------------
# For authentication
#-------------------
# we need this so that we can "import" login/logout/signup functions from auth.py
app.register_blueprint(auth, url_prefix='/')

# ---------------------------
# task REST api
# ---------------------------

@app.get('/api/tasks')
def get_tasks():
    'return a list of tasks sorted by submit/modify time'
    task_table = taskbook_db.get_table('task')
    tasks = [dict(x) for x in task_table.find(email=session['user_email'], order_by=['date', 'time'])]
    return { "tasks": tasks }

@app.post('/api/tasks',)
def create_task():
    'create a new task in the database'
    try:
        data = request.get_json()
        for key in data.keys():
            assert key in ["description", "date", "time", "important"], f"Illegal key '{key}'"
        assert type(data['description']) is str, "Description is not a string."
        assert len(data['description'].strip()) > 0, "Description is length zero."
    except Exception as e:
        print(400, str(e))
        return ("400 Bad Request:"+str(e), 400)
    try:
        task_table = taskbook_db.get_table('task')
        task_table.insert({
            "email":session['user_email'],
            "description":data['description'].strip(),
            "date":data['date'],
            "time":data['time'],
            "important":data['important'],
            "completed":False
        })
    except Exception as e:
        print(409, str(e))
        return ("409 Bad Request:"+str(e), 409)
    # return Success
    return {'status':200, 'success': True}

@app.put('/api/tasks')
def update_task():
    'update properties of an existing task in the database'
    try:
        data = request.get_json()
        for key in data.keys():
            assert key in ["id","description","completed", "date", "time", "important"], f"Illegal key '{key}'"
        assert type(data['id']) is int, f"id '{id}' is not int"
        if "description" in data:
            assert type(data['description']) is str, "Description is not a string."
            assert len(data['description'].strip()) > 0, "Description is length zero."
        if "completed" in data:
            assert type(data['completed']) is bool, "Completed is not a bool."
    except Exception as e:
        print(400, str(e))
        return ("400 Bad Request:"+str(e), 400)
    if 'date' in data:
        data['date'] = data['date']
    try:
        task_table = taskbook_db.get_table('task')
        task_table.update(row=data, keys=['id'])
    except Exception as e:
        print(409, str(e))
        return ("409 Bad Request:"+str(e), 409)
    # return Success
    return {'status':200, 'success': True}

@app.delete('/api/tasks')
def delete_task():
    'delete an existing task in the database'
    try:
        data = request.get_json()
        assert type(data['id']) is int, f"id '{id}' is not int"
    except Exception as e:
        print(400, str(e))
        return ("400 Bad Request:"+str(e), 400)
    try:
        task_table = taskbook_db.get_table('task')
        task_table.delete(id=data['id'], email=session['user_email'])
    except Exception as e:
        print(409, str(e))
        return ("409 Bad Request:"+str(e), 409)
    # return Success
    return {'status':200, 'success': True}

    #methods to handle errors for HTTP errors such as file not found and server errors
@app.errorhandler(HTTPException)
def handle_exception(e):
    #determine which type of exception occurred and redirect the user to the appropriate webpage
    if(isinstance(e,BadRequest)):
        return render_template("error400.html", data="Error 400: Page Not Found"),400
    elif(isinstance(e,NotFound)):
        return render_template("error404.html", data="Error 404: Bad Request"),404
    elif(isinstance(e,InternalServerError)):
        return render_template("error500.html", data="Error 500: Internal Server Error"),500
    else:
        return render_template("errorpage.html", data="Sorry, Something Went Wrong!"),e


