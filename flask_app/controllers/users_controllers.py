from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.model.user_model import User
from flask_app.model.workout_model import Workout
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
## bcrypt.generate_password_hash()
## bcrypt.check_password_hash(hashed_password, password_string)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/registration_page')
def index():
    if "user_id" in session:
        return redirect('/welcome')
    return render_template('registration.html')


@app.route('/welcome')
def success():
    if not "user_id" in session:
        return redirect('/registration_page')
    user = User.get_by_id({'id': session['user_id']})
    all_workouts = Workout.get_all()
    return render_template('welcome.html', user=user, all_workouts=all_workouts)


@app.route('/users/logout')
def logout():
    del session['user_id']
    return redirect('/registration_page')


@app.route('/register', methods=['POST'])  ## register() is an action route, so we need to redirect
def register():
    if not User.validate_user(request.form):
        return redirect('/registration_page')
    hashed_pw = bcrypt.generate_password_hash(request.form['password'])  ## if form data looks good, before creating a user -> hash the password. Access string we want to hash through request.form['password'] <- incoming password
    register_data = {           ## entered information from form
        **request.form,         ## copies whole form
        'password' : hashed_pw  ## key of password is now the hashed password
    }    
    
    ## if we don't instaniate the user here, and just pass the password instead-- the password is just plain text in password_confirmation
    ## if we pass it to our user, it get's trash collected, because we don't hold onto the password_confirmation in User.

    ## INSERT query returns id. Inside session[''] can be named whatever we want, but this makes sense. Right gives us back User id, and we store it in session -> logged in
    session['user_id'] = User.save(register_data) ## stores user's id for moving to other pages/if user id is logged in-- see on line 14, on index route
    return redirect('/welcome')


@app.route('/login', methods = ["POST"]) ## action -> needs redirect
def login():
    data = {
        'email' : request.form['email']
    }
    user_from_db = User.get_by_email(data) ## will either hold the user or return False if no user found -> models/get_by_email
    if not user_from_db:
        flash("Invalid Credentials", "log")
        return redirect('/registration_page')
    if not bcrypt.check_password_hash(user_from_db.password, request.form['password']): ## checking user_in_db's hashed password against entered password  --hashed password in register
        flash("Invalid Credentials", "log")
        return redirect('/registration_page')
    session["user_id"] = user_from_db.id  ## email was in db and password matches, so we store user's id in session
    return redirect('/welcome')


@app.route('/add/admin')
def add_admin_form():
    if not "user_id" in session:
        return redirect('/registration_page')
    all_users = User.get_all_users()
    return render_template('add_admin.html', all_users=all_users)

@app.route('/update/admin', methods=['POST'])
def add_admin():
    if not "user_id" in session:
        return redirect('/registration_page')
    data = {
        'id' : request.form['id']
    }
    User.create_admin(data)
    return redirect('/welcome')