from app import app, forms
from flask import session, redirect, url_for, render_template
import requests

applicationLayerDomain = "http://localhost:5001/"

def checkLoggedIn():
  return "id" in session

@app.route('/')
def index():
  if not checkLoggedIn():
    return redirect(url_for("login"))

  return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  if checkLoggedIn():
    return redirect(url_for("index"))

  form = forms.LoginForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    response = requests.post(applicationLayerDomain + "Sessions", json={"username": username, "password": password})
    if response:
      session["id"] = response.json()["id"]
      return redirect(url_for("index"))
    else:
      return render_template("login.html", form=form, validationError=response.json()["error"])

  return render_template("login.html", form=form, validationError=None)

@app.route("/register", methods=["GET", "POST"])
def register():
  if checkLoggedIn():
    return redirect(url_for("index"))

  form = forms.RegisterForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    response = requests.post(applicationLayerDomain + "Users", json={"username": username, "password": password})
    if response:
      session["id"] = response.json()["id"]
      return redirect(url_for("index"))
    else:
      return render_template("register.html", form=form, validationError=response.json()["error"])

  return render_template("register.html", form=form, validationError=None)
