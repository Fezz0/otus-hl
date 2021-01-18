from datetime import date, datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from model import Subscriber

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    search = [{"field": "email", "op": "=", "value": email}]
    subs = Subscriber.load(search, fields=["subscriber_id", "password_hash"])

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not subs or not check_password_hash(subs[0]["password_hash"], password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(subs[0], remember=remember)
    return redirect(url_for('main.profile'))


def parse_signup_form(form):
    signup_required_fields = (
        "email",
        "password",
        "first_name",
        "last_name"
    )

    data = {}
    data["email"] = form.get('email').lower() or None
    data["password"] = form.get('password').lower() or None
    data["first_name"] = form.get('first_name').lower() or None
    data["last_name"] = form.get('last_name').lower() or None

    birth_dt = form.get('birth_date') or None
    if birth_dt is not None:
        try:
            birth_dt = datetime.strptime(birth_dt, "%Y-%m-%d").date()
        except:
            birth_dt = None
    data["birth_dt"] = birth_dt

    data["sex"] = form.get('sex').lower() or None
    data["interests"] = form.get('interests').lower() or None
    data["city"] = form.get('city', None).lower() or None

    for k in signup_required_fields:
        if data.get(k) is None:
            raise ValueError(f"Field {k} is required but empty")

    return data


@auth.route('/signup')
def signup():
    return render_template('singup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    form_data = parse_signup_form(request.form)

    # Check If user exists
    search = [{"field": "email", "op": "=", "value": form_data["email"]}]
    subs = Subscriber.load(search, fields=["password_hash"])

    if subs:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    form_data["password_hash"] = generate_password_hash(form_data["password"], method='sha256')
    sub = Subscriber(**form_data)
    sub.save()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
