# ONLY FOR AUTH
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
import dataset 
# this one to hash the password during signup and check has during login
from werkzeug.security import generate_password_hash, check_password_hash

# to work with database in this file
taskbook_db = dataset.connect('sqlite:///taskbook.db')

# this lines makes it possible to write some routes here and include in app.py
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in and goes to /login, then send back to their default view
    if session.get('user_authenticated'):
        flash('Log out first to log back in.')
        cust_table = taskbook_db.get_table('customization')
        try:
            user_cust = cust_table.find_one(email=session['user_email'])
            default_view = user_cust['view']
            return redirect(url_for(default_view))
        except Exception as e:
            # No current View is set
            return redirect(url_for('dashboard'))

    if(request.method == 'GET'):
        return render_template("login.html")
    
    if(request.method == 'POST'):
        email = request.form.get('user_email')
        password = request.form.get('user_password')
        user_table = taskbook_db.get_table('user_cred')
        # first check if there is someone who is a user already
        user = user_table.find_one(email=email)
        if(user):
            # check_password_hash(a,b) will hash 'b' and check for equality with 'a', where 'a' is already hashed password
            if (check_password_hash(user['password'], password)):
                flash('Logged in successfully', category='success')
                # if password is correct, set sessions
                session['user_authenticated'] = True
                session['user_email'] = email
                cust_table = taskbook_db.get_table('customization')
                try:
                    user_cust = cust_table.find_one(email=session['user_email'])
                    default_view = user_cust['view']
                    return redirect(url_for(default_view))
                except Exception as e:
                    # No current View is set
                    return render_template('dashboard.html')
            else:
                flash('Incorrect password. Try again!', category='error')
        else:
            # if user does not exist then:
            flash('Email not registered. Please sign up first.', category='error')

    return render_template("login.html")


@auth.route('/logout')
def logout():
    # when log out clicked, unset the session variables
    if session.get('user_authenticated'):
        session.pop('user_email', None)
        session.pop('user_authenticated', None)
    else:
        # if someone tries to go to /logout then alert and send back to login.html
        flash('Please login first', category='error')
    return redirect(url_for('auth.login'))
    


@auth.route('/register', methods=['GET', 'POST'])
def register():
    # if user tries to sign up while logged in:
    if session.get('user_authenticated'):
        flash('Account already created')
        cust_table = taskbook_db.get_table('customization')
        try:
            user_cust = cust_table.find_one(email=session['user_email'])
            default_view = user_cust['view']
            return redirect(url_for(default_view))
        except Exception as e:
            # No current View is set
            return redirect(url_for('dashboard'))

    if(request.method == 'GET'):
        return render_template("register.html")

    if(request.method == 'POST'):
        # server-side validation seemed better with flash. so used this one instead of longer JS code
        email = request.form.get('user_email')
        password1 = request.form.get('user_password')
        password2 = request.form.get('confirm_password')
        security_question = request.form.get('security_question')
        security_answer = request.form.get('security_answer')

        if(len(email)<1):
            flash('Email cannot be empty', category='error')
        elif(password1 != password2):
            flash('Password do not match', category='error')
        elif(len(password1)<8):
            flash('Password must be at least 8 characters long', category='error')
        elif(len(security_question)<1):
            flash('Security question cannot be empty', category='error')
        elif(len(security_answer)<1):
            flash('Security answer cannot be empty', category='error')
        else:
            try:
                user_table = taskbook_db.get_table('user_cred')
                # first check if the user already exists
                user = user_table.find_one(email=email)
                if(user):
                    # flash alert and make them sign in again
                    flash('A user exists with that email address.', category='error')
                else:
                    # if new user, then hash the password, insert to table and log them in
                    hashed_password = generate_password_hash(password1, method='sha256')
                    user = dict(email=email, password=hashed_password, security_question=security_question, security_answer=security_answer)
                    user_table.insert(user)
                    flash('Sign up successful', category='success')
                    session['user_authenticated'] = True
                    session['user_email'] = email
                    # create customization entry for new user
                    cust_table = taskbook_db.get_table('customization')
                    user_cust = dict(email=email, view="dashboard", dark_mode=False, upcoming_shown=10, upcoming_type="task", week_view="dropdown", font_size="medium")
                    cust_table.insert(user_cust)
                    # redirect to dashboard page
                    return redirect(url_for('dashboard'))
            except Exception as e:
                print(409, str(e))
                return ("409 Bad Request:"+str(e), 409)

    return render_template('register.html')


@auth.route('/change_password', methods=['POST'])
def password_change():
    # if user is not logged in, then send back to login page
    if not session.get('user_authenticated'):
        flash('Please login first', category='error')
        return redirect(url_for('auth.login'))
    
    # if user is logged in, then change password

    try:
        email = session['user_email']
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if(new_password != confirm_password):
                flash('New passwords do not match', category='error')
                return redirect(url_for('settings'))

        if(len(new_password)<8):
                flash('New password must be at least 8 characters long', category='error')
                return redirect(url_for('settings'))

        if(new_password == current_password):
            flash('New password cannot be the same as the old password', category='error')
            return redirect(url_for('settings'))

        user_table = taskbook_db.get_table('user_cred')
        user = user_table.find_one(email=email)
        
        if(user):
            # check if current password is correct
            if (not check_password_hash(user['password'], current_password)):
                flash('Current password is incorrect', category='error')
                return redirect(url_for('settings'))

            user_table.update(dict(id=user['id'],password=generate_password_hash(new_password, method='sha256')), keys=['id'])
            flash('Password changed successfully', category='success')
            return redirect(url_for('settings'))

    except Exception as e:
        print(409, str(e))
        return ("409 Bad Request: "+str(e), 409)

    return redirect(url_for('settings'))

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    # if user is logged in, then send back to login page
    if(request.method == 'GET'):
        if session.get('user_authenticated'):
            flash('Change your password here or log out and click and forgot password on the login page', category='error')
            return redirect(url_for('settings'))
    
    if(request.method == 'POST'):
        try:
            user_email = request.form.get('email_to_change_password')
            security_answer = request.form.get('security_answer')
            new_password = request.form.get('new_password_1')
            confirm_password = request.form.get('new_password_2')

            if(new_password != confirm_password):
                flash('New passwords do not match', category='error')
                return redirect(url_for('auth.forgot_password'))

            if(len(new_password)<8):
                flash('New password must be at least 8 characters long', category='error')
                return redirect(url_for('auth.forgot_password'))

            user_table = taskbook_db.get_table('user_cred')
            user = user_table.find_one(email=user_email)
            if(not(user)):
                flash('User does not exist!',category='error')
                return redirect(url_for('auth.forgot_password'))
            
            if(not(user['security_answer'] == security_answer)):
                flash('Security answer is incorrect', category='error')
                return redirect(url_for('auth.forgot_password'))

            user_table.update(dict(id=user['id'], password=generate_password_hash(new_password, method='sha256')), keys=['id'])
            flash('Password changed successfully', category='success')
            return redirect(url_for('auth.login'))


        except Exception as e:
            print(409, str(e))
            return ("409 Bad Request: "+str(e), 409)

    return render_template("forgot_password.html")

@auth.get('/get_security_question')
def get_security_question():
    user_email = request.args.get('user_email')
    user_table = taskbook_db.get_table('user_cred')
    user = user_table.find_one(email=user_email)
    if(user):
        return {"question": user['security_question']}
    else:
        return {"question": "NA"}

@auth.post('/change_security_qa')
def change_security_qa():
    try:
        current_answer_from_user = request.form.get('current_answer')
        new_security_question = request.form.get('new_question')
        new_security_answer = request.form.get('new_answer')

        if(len(new_security_question) < 1):
            flash('Security question cannot be empty', category='error')
            return redirect(url_for('settings'))

        elif(len(new_security_answer) < 1):
            flash('Security answer cannot be empty', category='error')
            return redirect(url_for('settings'))

        user_table = taskbook_db.get_table('user_cred')
        user = user_table.find_one(email=session['user_email'])
        if(user):
            # check if current password is correct
            current_answer = user['security_answer']
            if (not current_answer == current_answer_from_user):
                flash('Incorrect answer. Try again.', category='error')
                return redirect(url_for('settings'))
            
            user_table.update(dict(id=user['id'], security_question=new_security_question, security_answer=new_security_answer), keys=['id'])
            flash('Security question and answer updated!', category='success')
            return redirect(url_for('settings'))

        else:
            flash('Something went wrong. Try again!', category='error')
            return redirect(url_for('settings'))

    except Exception as e:
        print(409, str(e))
        return ("409 Bad Request: "+str(e), 409)