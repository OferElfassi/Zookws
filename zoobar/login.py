from flask import g, redirect, render_template, request, url_for, Markup
from functools import wraps
import debug
from zoodb import *
import time
import auth
import bank
import random
import auth_client
import bank_client
from datetime import datetime, timedelta


class User(object):
    def __init__(self):
        self.zoobars = 0
        self.token = None
        self.person = None

    def checkLogin(self, username, password, blocking_duration_minutes=2, max_attempts=5):
        now = datetime.now()
        cred = Cred.get_by_username(username)
        if cred is None:
            return None
        # Get all failed attempts that happened in the last blocking_duration_minutes minutes
        attempts = FailedLogin.get_failed_attempts(cred, now, blocking_duration_minutes)
        if len(attempts) >= max_attempts:  # Too many failed attempts
            time_left = get_remaining_time(attempts, now, blocking_duration_minutes)
            login_error = "Too many failed attempts. Try again in %s:%s" % (
                time_left.seconds // 60, time_left.seconds % 60)
            log(login_error)
            return login_error
        # Check credentials

        token = auth_client.login(username, password)
        if token is not None:  # Successful login
            # Clear failed attempts
            FailedLogin.delete_failed_attempts(attempts)
            return self.loginCookie(username, token)
        else:  # Failed login
            FailedLogin.add_failed_attempt(cred)  # Log failure to failed attempts table
            time.sleep(1)  # Sleep for 1 second to prevent brute force attacks
            return None

    def loginCookie(self, username, token):
        self.setPerson(username, token)
        return "%s#%s" % (username, token)

    def logout(self):
        self.person = None

    def addRegistration(self, username, password):
        token = auth_client.register(username, password)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def checkCookie(self, cookie):
        if not cookie:
            return
        (username, token) = cookie.rsplit("#", 1)
        if auth_client.check_token(username, token):
            self.setPerson(username, token)

    def setPerson(self, username, token):
        persondb = person_setup()
        self.person = persondb.query(Person).get(username)
        self.token = token
        self.zoobars = bank_client.balance(username)


def logged_in():
    g.user = User()
    g.user.checkCookie(request.cookies.get("PyZoobarLogin"))
    if g.user.person:
        return True
    else:
        return False


def requirelogin(page):
    @wraps(page)
    def loginhelper(*args, **kwargs):
        if not logged_in():
            return redirect(url_for('login') + "?nexturl=" + request.url)
        else:
            return page(*args, **kwargs)

    return loginhelper


# Calculate remaining time until the blocking period ends
def get_remaining_time(attempts, time_ref, blocking_duration_minutes):
    blocking_end_time = attempts[-1].timestamp + timedelta(minutes=blocking_duration_minutes)
    blocking_remaining_time = blocking_end_time - time_ref
    return blocking_remaining_time


@catch_err
def login():
    cookie = None
    login_error = ""
    user = User()

    if request.method == 'POST':
        username = request.form.get('login_username')
        password = request.form.get('login_password')

        if 'submit_registration' in request.form:
            if not username:
                login_error = "You must supply a username to register."
            elif not password:
                login_error = "You must supply a password to register."
            else:
                cookie = user.addRegistration(username, password)
                if not cookie:
                    login_error = "Registration failed."
        elif 'submit_login' in request.form:
            if not username:
                login_error = "You must supply a username to log in."
            elif not password:
                login_error = "You must supply a password to log in."
            else:
                cookie = user.checkLogin(username, password)
                if not cookie:
                    login_error = "Invalid username or password."
                elif "Too many failed attempts" in cookie:
                    login_error = cookie
                    cookie = None

    nexturl = request.values.get('nexturl', url_for('index'))
    if cookie:
        response = redirect(nexturl)
        ## Be careful not to include semicolons in cookie value; see
        ## https://github.com/mitsuhiko/werkzeug/issues/226 for more
        ## details.
        response.set_cookie('PyZoobarLogin', cookie)
        return response

    return render_template('login.html',
                           nexturl=nexturl,
                           login_error=login_error,
                           login_username=Markup(request.form.get('login_username', '')))


@catch_err
def logout():
    if logged_in():
        g.user.logout()
    response = redirect(url_for('login'))
    response.set_cookie('PyZoobarLogin', '')
    return response
