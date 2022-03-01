# SWIFT Taskbook
# Web Application for Task Management

# flask web objects
from auth import auth
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
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

# ---------------------------
# account API
# ---------------------------

@app.delete('/api/account')
def delete_account():
    'verification'
    data = request.get_json()
    user_table = taskbook_db.get_table('user_cred')
    if data['email'] != session['user_email']:
        return ("Incorrect Email", 409)
    try:
        user = user_table.find_one(email=data['email'])
        if(not check_password_hash(user['password'], data['passwd'])):
            return("Invalid Credentials", 409)
    except Exception as e:
        print(409, str(e))
        return ("409 Bad Request:"+str(e), 409)
    
    task_table = taskbook_db.get_table('task')
    cust_table = taskbook_db.get_table('customization')
    
    # Deletion Selection, then droping entrys from the table
    if data['del_type'] == "settings":
        try:
            user_cust = dict(email=session['user_email'], view="dashboard", dark_mode=False, upcoming_shown=10, upcoming_type="task", week_view="dropdown", font_size="medium")
            cust_table.update(user_cust, ['email'])
            flash("All settings reset")
            return {'status':200, 'success': True}
        except Exception as e:
            print(409, str(e))
    elif data['del_type'] == "tasks":
        try:
            task_table.delete(email=session['user_email'])
            flash("All tasks deleted")
            return {'status':200, 'success': True}
        except Exception as e:
            print(409, str(e))
    elif data['del_type'] == "account":
        try:
            cust_table.delete(email=session['user_email'])
            task_table.delete(email=session['user_email'])
            user_table.delete(email=session['user_email'])
            session.clear()
            flash("Account successfully deleted!")
            return {'status':200, 'success': True}
        except Exception as e:
            print(409, str(e))
    
    return ("409 Bad Request: Invalid selection" + data['del_type'], 409)
#get customization settings for settings page
@app.get('/api/settings')
def get_settings():
    'return customization settings for the user'
    customization_table = taskbook_db.get_table('customization')
    settings = [dict(x) for x in customization_table.find(email=session['user_email'])]
    return { "settings": settings }

#change customization settings for settings page
@app.post('/api/settings')
def update_settings():
    'update customization settings in database'
    customization_table = taskbook_db.get_table('customization')
    new_upcoming_type = request.form.get('new_upcoming_type')
    new_upcoming_shown = request.form.get('new_upcoming_shown')
    new_view = request.form.get('default_view')
    user = customization_table.find_one(email=session['user_email'])
    if(user):
        customization_table.update(dict(id=user['id'], view=new_view, upcoming_type=new_upcoming_type, upcoming_shown=new_upcoming_shown), keys=['id'])
    return redirect(url_for('settings'))

#methods to handle errors for HTTP errors such as file not found and server errors
@app.errorhandler(HTTPException)
def handle_exception(e):
    #determine which type of exception occurred and redirect the user to the appropriate webpage
    if(isinstance(e,BadRequest)):
        return render_template("errorpage.html", data="Error 400: Bad Request"),400
    elif(isinstance(e,NotFound)):
        return render_template("errorpage.html", data="Error 404: Page Not Found"),404
    elif(isinstance(e,InternalServerError)):
        return render_template("errorpage.html", data="Error 500: Internal Server Error"),500
    else:
        return render_template("errorpage.html", data="Sorry, Something Went Wrong!"),e


