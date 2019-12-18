from app import app, forms
from flask import session, redirect, url_for, render_template, jsonify, flash
import requests
from requests.auth import HTTPBasicAuth

applicationLayerDomain = "http://localhost:5001/"

def checkLoggedIn():
  return "user" in session

@app.route("/")
def index():
  if not checkLoggedIn():
    return redirect(url_for("login"))

  booksList = []

  userReadBooksResponse = requests.get(applicationLayerDomain + "UserReadBooks?userId=" + session["user"]["id"], auth=HTTPBasicAuth(session["user"]["username"], session["user"]["password"]))
  if userReadBooksResponse:
    userReadBooksJSON = userReadBooksResponse.json()
    if not userReadBooksJSON:
      #if user has read no books
      return render_template("index.html", error=None, booksList=booksList, numberOfDummyCards=None, userBookDetails=None, endpoint=applicationLayerDomain, user=session["user"])
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
      while booksListLength % 2 != 0:
        numberOfDummyCards += 1
        booksListLength += 1

      userBookDetails = {}
      for userReadBook in userReadBooksJSON:
        userBookDetails[userReadBook["bookId"]] = {"id": userReadBook["id"], "favourite": userReadBook["favourite"], "thoughts": userReadBook["thoughts"]}

      return render_template("index.html", error=None, booksList=booksList, numberOfDummyCards=numberOfDummyCards, userBookDetails=userBookDetails, endpoint=applicationLayerDomain, user=session["user"])
  else:
    #error has occurred
    return render_template("index.html", error=userReadBooksResponse.json()["error"], booksList=booksList, numberOfDummyCards=None, userBookDetails=None, endpoint=applicationLayerDomain, user=session["user"])

  return render_template("index.html", error=None, booksList=booksList, numberOfDummyCards=None, userBookDetails=None, endpoint=applicationLayerDomain, user=session["user"])

@app.route("/favouriteBooks")
def favouriteBooks():
  if not checkLoggedIn():
    return redirect(url_for("login"))

  favouriteBooksList = []

  userReadBooksResponse = requests.get(applicationLayerDomain + "UserReadBooks?userId=" + session["user"]["id"] + "&favourite=1", auth=HTTPBasicAuth(session["user"]["username"], session["user"]["password"]))
  if userReadBooksResponse:
    userReadBooksJSON = userReadBooksResponse.json()
    if not userReadBooksJSON:
      #if user has read no books
      return render_template("favouriteBooks.html", error=None, booksList=favouriteBooksList, numberOfDummyCards=None, userBookDetails=None, endpoint=applicationLayerDomain, user=session["user"])
    else:
      #if user has read books

      #get details of read books
      listOfBookIds = []
      for userReadBook in userReadBooksJSON:
        listOfBookIds.append(userReadBook["bookId"])
      booksResponse = requests.get(applicationLayerDomain + "Books", json=listOfBookIds, auth=HTTPBasicAuth(session["user"]["username"], session["user"]["password"]))
      favouriteBooksList = booksResponse.json()

      booksListLength = len(favouriteBooksList)
      numberOfDummyCards = 0
      while booksListLength % 2 != 0:
        numberOfDummyCards += 1
        booksListLength += 1

      userBookDetails = {}
      for userReadBook in userReadBooksJSON:
        userBookDetails[userReadBook["bookId"]] = {"id": userReadBook["id"], "favourite": userReadBook["favourite"], "thoughts": userReadBook["thoughts"]}

      return render_template("favouriteBooks.html", error=None, booksList=favouriteBooksList, numberOfDummyCards=numberOfDummyCards, userBookDetails=userBookDetails, endpoint=applicationLayerDomain, user=session["user"])
  else:
    #error has occurred
    return render_template("favouriteBooks.html", error=userReadBooksResponse.json()["error"], booksList=favouriteBooksList, numberOfDummyCards=None, userBookDetails=None, endpoint=applicationLayerDomain, user=session["user"])

  return render_template("favouriteBooks.html", error=None, booksList=favouriteBooksList, numberOfDummyCards=None, userBookDetails=None, endpoint=applicationLayerDomain, user=session["user"])

@app.route("/changePassword", methods=["GET", "POST"])
def changePassword():
  if not checkLoggedIn():
    return redirect(url_for("login"))

  form = forms.changePasswordForm()

  if form.validate_on_submit():
    newPassword = form.newPassword.data
    response = requests.put(applicationLayerDomain + "Users/" + session["user"]["id"], json={"password": newPassword}, auth=HTTPBasicAuth(session["user"]["username"], session["user"]["password"]))
    if response:
      #do alert
      session["user"] = {"id": session["user"]["id"], "username": session["user"]["username"], "password": newPassword}
      flash("Your password was successfully changed!")
      return redirect(url_for("changePassword"))
    else:
      return render_template("changePassword.html", form=form, validationError=response.json()["error"])

  return render_template("changePassword.html", form=form, validationError=None)

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
