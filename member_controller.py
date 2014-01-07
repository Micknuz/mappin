import hmac
import hashlib
import datetime
import flask
from flask import Flask, request, render_template, redirect, url_for, g, flash
from functools import wraps

from model import Person, Password
import db
import utils

from _exceptions import *

def current_user():
    try:
        return g._CURRENT_USER
    except AttributeError:
        pass

    try:
        cookie = flask.request.cookies["ygo_user"]
    except KeyError:
        return

    try:
        id, hash = cookie.split(",", 1)
    except ValueError:
        return

    if hash == hmac.new(app.secret_key, id, hashlib.sha1).hexdigest():
        g._CURRENT_USER = db.session.query(Person).filter_by(id=id).first()
        return g._CURRENT_USER


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def privileged(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for('login', next=request.url))
        if current_user().privileged is not True:
            return utils.redirect_back('map_list')
        return f(*args, **kwargs)
    return decorated_function

from mappin import app


def _login(person, next_url="/"):
    response = flask.redirect(next_url)
    h = hmac.new(app.secret_key, str(person.id), hashlib.sha1)
    cookie = "{0},{1}".format(person.id, h.hexdigest())
    auto = request.values.get("auto_login", False)
    expires = datetime.datetime.utcnow() + datetime.timedelta(31)
    response.set_cookie("ygo_user", cookie,
                        expires=expires if auto else None,
                        path="/")
    return response


@app.route("/join", methods=["POST", "GET"])
def join():
    if request.method == "POST":
        name = request.values.get("name")
        password = request.values.get("password")
        privileged = request.values.get("privileged") is 'on'
        user = Person(id=name, password_hash=Password.hash(password),
                      privileged=privileged)
        db.session.add(user)
        db.session.commit()
        return _login(user)
    elif request.method == "GET":
        return render_template("join.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user():
        return redirect("/")
    if request.method == "POST":
        name = request.values.get("name")
        password = request.values.get("password")
        person = db.session.query(Person).filter_by(id=name).first()
        if person.password == password:
            return _login(person)
        raise PasswordMisMatch
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/logout")
def logout():
    response = flask.redirect("/")
    response.set_cookie("ygo_user", "",
                        expires=datetime.datetime.utcnow(),
                        path="/")
    return response

@app.before_request
def before_request():
    g.user = current_user()

@app.after_request
def shutdown_session(resp):
    db.session.remove()
    return resp


