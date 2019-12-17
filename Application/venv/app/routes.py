from app import app, models, db
from flask import make_response, request, jsonify
import uuid
import json
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from passlib.hash import bcrypt
from flask_cors import CORS

api = Api(app)
CORS(app)
auth = HTTPBasicAuth()

@auth.verify_password
def verifyPassword(username, password):
  #check username exists
  potentialUser = models.User.query.filter_by(username=username).first()
  if not potentialUser:
    return False
  
  #check valid password
  if not bcrypt.verify(password, potentialUser.password):
    return False

  #return user
  return True

def checkPostData(dictToCheck, *attributes):
  for dictItem in dictToCheck:
    if dictItem not in attributes:
      return False
  return True

def checkEssentialPostData(dictToCheck, *essentialAttributes):
  for attribute in essentialAttributes:
    if attribute not in dictToCheck:
      return False
  return True

def checkFilterAttributes(filterDict, *attributes):
  for filterItem in filterDict:
    if filterItem not in attributes:
      return False
  return True

class UserResource(Resource):

  @auth.login_required
  def get(self, userId):
    user = models.User.query.filter_by(id=userId).first()
    if user:
      return user.toJSON(), 200
    else:
      return {"error": "No user has the specified ID"}, 404
  
  #to change user password
  @auth.login_required
  def put(self, userId):
    data = request.get_json()
    if checkPostData(data, "password"):
      user = models.User.query.filter_by(id=userId).first()
      if user:
        #check if password is in use
        for user in models.User.query.all():
          if bcrypt.verify(data["password"], user.password):
            return {"error": "New password already in use"}, 409

        user.password = bcrypt.hash(data["password"])
        db.session.commit()

      else:
        return {"error": "No user has the specified ID"}, 404

    else:
      return {"error": "JSON does not include the required data to make a new user"}, 400

class UsersResource(Resource):

  def post(self):
    data = request.get_json()
    #check json data is all there
    if checkPostData(data, "username", "password"):

      #check if username is being used
      if models.User.query.filter_by(username=data["username"]).first():
        return {"error": "Username already in use"}, 409

      #check if password is in use
      for user in models.User.query.all():
        if bcrypt.verify(data["password"], user.password):
          return {"error": "Password already in use"}, 409
      
      #add user to database
      newUserId = uuid.uuid1().hex
      newUser = models.User(id=newUserId, username=data["username"], password=bcrypt.hash(data["password"]))
      db.session.add(newUser)
      db.session.commit()
      return {"id": newUser.id, "username": newUser.username, "password": data["password"]}, 201

    else:
      return {"error": "JSON does not include the required data to make a new user"}, 400

class BookResource(Resource):

  @auth.login_required
  def get(self, bookId):
    book = models.Book.query.filter_by(id=bookId).first()
    if book:
      return book.toJSON(), 200
    else:
      return {"error": "No book has the specified ID"}, 404

class BooksResource(Resource):

  @auth.login_required
  def get(self):
    booksList = []
    #if there is json data sent along with the get then this is a list of specific book IDs so send back those books
    if request.get_json():
      for book in models.Book.query.filter(models.Book.id.in_(request.get_json())).all():
        booksList.append(book.toJSON())
      return booksList, 200

    #if there are not request arguments or those arguments are not for filtering (e.g. a callback argument)
    if not request.args or not checkFilterAttributes(request.args, "ISBN", "title", "author"):
      for book in models.Book.query.all():
        #get all books
        booksList.append(book.toJSON())
    
    else:
      if "ISBN" in request.args:
        filterText = "%{}%".format(request.args["ISBN"])
        for book in models.Book.query.filter(models.Book.ISBN.like(filterText)).all():
          booksList.append(book.toJSON())
      elif "title" in request.args:
        filterText = "%{}%".format(request.args["title"])
        for book in models.Book.query.filter(models.Book.title.like(filterText)).all():
          booksList.append(book.toJSON())
      elif "author" in request.args:
        filterText = "%{}%".format(request.args["author"])
        for book in models.Book.query.filter(models.Book.author.like(filterText)).all():
          booksList.append(book.toJSON())
    
    return booksList, 200
  
  def post(self):
    data = request.get_json()
    if checkPostData(data, "ISBN", "title", "author", "publishedDate", "description", "coverImageURI"):
      if checkEssentialPostData(data, "ISBN", "title", "author"):
        potentialBook = models.Book.query.filter_by(ISBN=data["ISBN"]).first()
        if potentialBook:
          return {"error": "ISBN already belongs to an existing book"}, 409
        
        newBookId = uuid.uuid1().hex
        newBook = models.Book(id=newBookId, ISBN=data["ISBN"], title=data["title"], author=data["author"])
        if "publishedDate" in data:
          newBook.publishedDate = data["publishedDate"]
        if "description" in data:
          newBook.description = data["description"]
        if "coverImageURI" in data:
          newBook.coverImageURI = data["coverImageURI"]
        
        db.session.add(newBook)
        db.session.commit()
        return newBook.toJSON(), 201

    else:
      return {"error": "JSON does not include the required data to create a book"}, 400    

class UserReadBookResource(Resource):

  @auth.login_required
  def get(self, userReadBookId):
    userReadBook = models.UserReadBook.query.filter_by(id=userReadBookId).first()
    if userReadBook:
      return userReadBook.toJSON(), 200
    else:
      return {"error": "No userReadBook has the specified ID"}, 404

  @auth.login_required
  def put(self, userReadBookId):
    userReadBookToChange = models.UserReadBook.query.filter_by(id=userReadBookId).first()
    if userReadBookToChange:
      #only allowed to change the favourite and thoughts attributes so only check for them
      data = request.get_json()
      if "favourite" in data:
        userReadBookToChange.favourite = data["favourite"]
      if "thoughts" in data:
        userReadBookToChange.thoughts = data["thoughts"]
      
      #commmit changes
      db.session.commit()
      return userReadBookToChange.toJSON(), 204

    else:
      return {"error": "No userReadBook has the specified ID"}, 404

class UserReadBooksResource(Resource):

  @auth.login_required
  def get(self):
    userReadBooksList = []
    if not request.args or not checkFilterAttributes(request.args, "userId", "bookId"):
      for userReadBook in models.UserReadBook.query.all():
        #get all userReadBooks
        userReadBooksList.append(userReadBook.toJSON())
    
    else:
      if "userId" in request.args:
        for userReadBook in models.UserReadBook.query.filter_by(userId=request.args["userId"]).all():
          userReadBooksList.append(userReadBook.toJSON())
      if "bookId" in request.args:
        for userReadBook in models.UserReadBook.query.filter_by(bookId=request.args["bookId"]).all():
          userReadBooksList.append(userReadBook.toJSON())
    
    return userReadBooksList, 200

  @auth.login_required
  def post(self):
    data = request.get_json()
    if checkPostData(data, "userId", "bookId", "favourite", "thoughts"):
      if checkEssentialPostData(data, "userId", "bookId", "favourite"):
        potentialUserReadBooks = models.UserReadBook.query.filter_by(userId=data["userId"]).all()
        for potentialUserReadBook in potentialUserReadBooks:
          if potentialUserReadBook.bookId == data["bookId"]:
            return {"error": "User has already said they have read this book"}, 409
        
        newUserReadBookId = uuid.uuid1().hex
        newUserReadBook = models.UserReadBook(id=newUserReadBookId, userId=data["userId"], bookId=data["bookId"], favourite=data["favourite"])
        if "thoughts" in data:
          newUserReadBook.thoughts = data["thoughts"]
        
        db.session.add(newUserReadBook)
        db.session.commit()
        return newUserReadBook.toJSON(), 201

    else:
      return {"error": "JSON does not include the required data to create a UserReadBook resource"}, 400


class SessionsResource(Resource):

  def post(self):
    data = request.get_json()
    if checkPostData(data, "username", "password"):

      #check username exists
      potentialUser = models.User.query.filter_by(username=data["username"]).first()
      if not potentialUser:
        return {"error": "Invalid credentials"}, 401
      
      #check valid password
      if not bcrypt.verify(data["password"], potentialUser.password):
        return {"error": "Invalid credentials"}, 401

      #return user
      return {"id": potentialUser.id, "username": potentialUser.username, "password": data["password"]}, 201
    
    else:
      return {"error": "JSON does not include the required data to authenticate a user"}, 400


api.add_resource(UserResource, "/Users/<string:userId>")
api.add_resource(UsersResource, "/Users")
api.add_resource(BookResource, "/Books/<string:bookId>")
api.add_resource(BooksResource, "/Books")
api.add_resource(UserReadBookResource, "/UserReadBooks/<string:userReadBookId>")
api.add_resource(UserReadBooksResource, "/UserReadBooks")
api.add_resource(SessionsResource, "/Sessions")