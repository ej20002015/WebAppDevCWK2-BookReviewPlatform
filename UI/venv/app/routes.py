from app import app, forms
from flask import session, redirect, url_for, render_template, jsonify
import requests
from requests.auth import HTTPBasicAuth

applicationLayerDomain = "http://localhost:5001/"

def checkLoggedIn():
  return "user" in session

@app.route('/')
def index():
  if not checkLoggedIn():
    return redirect(url_for("login"))

  booksList = []

  userReadBooksResponse = requests.get(applicationLayerDomain + "UserReadBooks?userId=" + session["user"]["id"], auth=HTTPBasicAuth(session["user"]["username"], session["user"]["password"]))
  if userReadBooksResponse:
    userReadBooksJSON = userReadBooksResponse.json()
    if not userReadBooksJSON:
      #if user has read no books
      print("read no books")
      return render_template("index.html", error=None, booksList=booksList, numberOfDummyCards=None)
    else:
      #if user has read books

      #get details of read books
      listOfBookIds = []
      for userReadBook in userReadBooksJSON:
        listOfBookIds.append(userReadBook["bookId"])
      booksResponse = requests.get(applicationLayerDomain + "Books", json=listOfBookIds, auth=HTTPBasicAuth(session["user"]["username"], session["user"]["password"]))
      booksList = booksResponse.json()
      booksListLength = len(booksList)
      numberOfDummyCards = 0
      while booksListLength % 3 != 0:
        numberOfDummyCards += 1
        booksListLength += 1
      return render_template("index.html", error=None, booksList=booksList, numberOfDummyCards=numberOfDummyCards)
  else:
    #error has occurred
    return render_template("index.html", error=userReadBooksResponse.json()["error"], booksList=booksList, numberOfDummyCards=None)

  return render_template("index.html", error=None, booksList=booksList, numberOfDummyCards=None)

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
      session["user"] = response.json()
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
      session["user"] = response.json()
      return redirect(url_for("index"))
    else:
      return render_template("register.html", form=form, validationError=response.json()["error"])

  return render_template("register.html", form=form, validationError=None)

@app.route("/newBook", methods=["GET"])
def newBook():
  if not checkLoggedIn():
    return redirect(url_for("login")) 

  return render_template("newBook.html", endpoint=applicationLayerDomain, user=session["user"])

@app.route("/test")
def test():
  if not checkLoggedIn():
    return redirect(url_for("login"))

  #data = {"userId": "74c15a761f9811ea99ff5800e3e11c5d", "bookId": "9d4c5e6c-1f9a-11ea-99ff-5800e3e11c5d"}
  response = requests.get(applicationLayerDomain + "UserReadBooks/acfaa3a81fa611ea99ff5800e3e11c5d", auth=HTTPBasicAuth(session["user"]["username"], session["user"]["password"]))
  print(response)
  if response:
    return jsonify(response.json())
  else:
    return response.json()["error"]
