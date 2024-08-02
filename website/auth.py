from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)
WebsiteName = "The Study Resource"

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #if the username and password match login
        #else error messages
        email = request.form.get('email').lower()
        password = request.form.get('password')
        #check all values in user where email column = email
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User.query.filter_by(username=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Login Successful', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('incorrect password', category='error')
        else:
            flash('User does not exist', category='error')
    return render_template("login.html", WebsiteName=WebsiteName)

@auth.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        email = request.form.get('email').lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        studying = request.form.get('studying')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email in use', category='error')
        elif len(email) < 4:
            flash("email to short", category='error')
        elif len(username) < 2:
            flash("username to short", category='error')
        elif password != confirm_password:
            flash("passwords dont match", category='error')
        elif len(password) < 7:
            flash("password to short", category='error')
        else:
            #addUser
            new_user = User(email=email.lower(), username=username.lower(), password=generate_password_hash(password, method='pbkdf2:sha256'), studying=studying)
            db.session().add(new_user)
            db.session.commit()
            flash("Welcome", category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))



    return render_template("createAccount.html", WebsiteName=WebsiteName)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

