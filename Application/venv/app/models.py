from app import db
import json

class User(db.Model):
  #id will be a 128 bit unique number generated using UUID
  id = db.Column(db.String(36), primary_key=True)
  username = db.Column(db.String(100), nullable=False)
  #password will be a hashed and salted cypher text generated using the bcrypt algorithm
  password = db.Column(db.String(60), nullable=False)

  books = db.relationship("Book", secondary="user_read_book")

  def toJSON(self):
    return {"id": self.id, "username": self.username, "password": self.password}

class Book(db.Model):
  #id will be a 128 bit unique number generated using UUID
  id = db.Column(db.String(36), primary_key=True)
  ISBN = db.Column(db.String(13), unique=True)
  title = db.Column(db.Text, nullable=False)
  author = db.Column(db.Text, nullable=False)
  publishedDate = db.Column(db.String(50))
  description = db.Column(db.Text)
  coverImageURI = db.Column(db.Text)

  users = db.relationship("User", secondary="user_read_book")

  def toJSON(self):
    return {"id": self.id, "ISBN": self.ISBN, "title": self.title, "author": self.author, "publishedDate": self.publishedDate, "description": self.description, "coverImageURI": self.coverImageURI}

class UserReadBook(db.Model):
  #id will be a 128 bit unique number generated using UUID
  id = db.Column(db.String(36), primary_key=True)
  userId = db.Column(db.String(36), db.ForeignKey("user.id"))
  bookId = db.Column(db.String(36), db.ForeignKey("book.id"))
  favourite = db.Column(db.Boolean, nullable=False)
  thoughts = db.Column(db.Text)

  def toJSON(self):
    return {"id": self.id, "userId": self.userId, "bookId": self.bookId, "favourite": self.favourite, "thoughts": self.thoughts}


