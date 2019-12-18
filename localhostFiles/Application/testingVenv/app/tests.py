import requests
from requests.auth import HTTPBasicAuth
import unittest
import uuid
import os
from random import randint

randintUpperLimit = 9999999999999

applicationLayerDomain = "http://localhost:5001/"
testUsers = []
testBooks = []
testUserReadBooks = []

class LogInTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if not testUsers:
      testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
      testUsers[-1]["id"] = response.json()["id"]

  def testLogin(self):
    response = requests.post(applicationLayerDomain + "Sessions", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
    assert response, "Server should have validated the test users credentials as correct SERVER RESPONSE=" + str(response)
  
  def testInvalidPassword(self):
    response = requests.post(applicationLayerDomain + "Sessions", json={"username": testUsers[-1]["username"], "password": uuid.uuid1().hex})
    assert response.status_code == 401, "Server should have validated the test users credentials as incorrect SERVER RESPONSE=" + str(response)

  def testInvalidUsername(self):
    response = requests.post(applicationLayerDomain + "Sessions", json={"username": uuid.uuid1().hex, "password": testUsers[-1]["password"]})
    assert response.status_code == 401, "Server should have validated the test users credentials as incorrect SERVER RESPONSE=" + str(response)

  def testLoginWithNotEnoughDetails(self):
    response = requests.post(applicationLayerDomain + "Sessions", json={"username": uuid.uuid1().hex})
    assert response.status_code == 400, "Server should have validated the test users credentials as incorrect SERVER RESPONSE=" + str(response)

class RegisterTests(unittest.TestCase):

  def testRegister(self):
    testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
    response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
    testUsers[-1]["id"] = response.json()["id"]
    assert response, "Test user could not register with details: " + str(testUsers[-1]) + " SERVER RESPONSE=" + str(response)
  
  def testRegisterWithExistingUsername(self):
    response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": uuid.uuid1().hex})
    assert response.status_code == 409, "Server should give a 409 error for a username already being used SERVER RESPONSE=" + str(response)

  def testRegisterWithExistingPassword(self):
    response = requests.post(applicationLayerDomain + "Users", json={"username": uuid.uuid1().hex, "password": testUsers[-1]["password"]})
    assert response.status_code == 409, "Server should give a 409 error for a password already being used SERVER RESPONSE=" + str(response)
  
  def testRegisterWithNotEnoughDetails(self):
    response = requests.post(applicationLayerDomain + "Users", json={"username": uuid.uuid1().hex})
    assert response.status_code == 400, "Server should give a 400 error for passing in not enough data to make a new user SERVER RESPONSE=" + str(response)

class UserTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if not testUsers:
      testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
      testUsers[-1]["id"] = response.json()["id"]

  def testGetUser(self):
    response = requests.get(applicationLayerDomain + "Users/" + testUsers[-1]["id"], auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response, "Server should have returned the correct user resource SERVER RESPONSE=" + str(response)
  
  def testGetInvalidId(self):
    response = requests.get(applicationLayerDomain + "Users/" + uuid.uuid1().hex, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response.status_code == 404, "Server should not have returned any user SERVER RESPONSE=" + str(response)

  def changePassword(self):
    data = {"password": uuid.uuid1().hex}
    response = requests.put(applicationLayerDomain + "Users/" + testUsers[-1]["id"], json=data, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response.status_code == 204 and response.json()["password"] == data["password"], "Server should have changed the password of the user SERVER RESPONSE=" + str(response)

class BooksTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if not testUsers:
      testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
      testUsers[-1]["id"] = response.json()["id"]
  
  def testNewBook(self):
    testBooks.append({"ISBN": randint(0, randintUpperLimit), "title": uuid.uuid1().hex, "author": uuid.uuid1().hex})
    response = requests.post(applicationLayerDomain + "Books", json={"ISBN": testBooks[-1]["ISBN"], "title": testBooks[-1]["title"], "author": testBooks[-1]["author"]}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    testBooks[-1]["id"] = response.json()["id"]
    assert response, "Could not create book SERVER RESPONSE=" + str(response)

  def testGetAllBooks(self):
    if not testBooks:
      testBooks.append({"ISBN": randint(0, randintUpperLimit), "title": uuid.uuid1().hex, "author": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Books", json={"ISBN": testBooks[-1]["ISBN"], "title": testBooks[-1]["title"], "author": testBooks[-1]["author"]})
      testBooks[-1]["id"] = response.json()["id"]

    response = requests.get(applicationLayerDomain + "Books", auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response and response.json(), "No books retrieved SERVER RESPONSE=" + str(response)
    bookFound = False
    for book in response.json():
      if book["id"] == testBooks[-1]["id"]:
        bookFound = True
    assert bookFound, "Can't find recently created book in list of all books SERVER RESPONSE=" + str(response)
  
  def testCreateBookWithNotEnoughDetails(self):
    response = requests.post(applicationLayerDomain + "Books", json={"ISBN": "Doesn't matter", "title": "Doesn't matter"}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response.status_code == 400, "POST should have responded with a 400 code to say there is not enough data to make a new book SERVER RESPONSE=" + str(response)

class BookTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if not testUsers:
      testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
      testUsers[-1]["id"] = response.json()["id"]
    if not testBooks:
      testBooks.append({"ISBN": randint(0, randintUpperLimit), "title": uuid.uuid1().hex, "author": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Books", json={"ISBN": testBooks[-1]["ISBN"], "title": testBooks[-1]["title"], "author": testBooks[-1]["author"]}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
      testBooks[-1]["id"] = response.json()["id"]
  
  def testGetBook(self):
    response = requests.get(applicationLayerDomain + "Books/" + testBooks[-1]["id"], auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response, "get request should have returned a book SERVER RESPONSE=" + str(response)

  def testGetInvalidBook(self):
    response = requests.get(applicationLayerDomain + "Books/2", auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response.status_code == 404, "get request should not have returned a book SERVER RESPONSE=" + str(response)

class UserReadBooksTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if not testUsers:
      testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
      testUsers[-1]["id"] = response.json()["id"]
    if not testBooks:
      testBooks.append({"ISBN": randint(0, randintUpperLimit), "title": uuid.uuid1().hex, "author": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Books", json={"ISBN": testBooks[-1]["ISBN"], "title": testBooks[-1]["title"], "author": testBooks[-1]["author"]}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
      testBooks[-1]["id"] = response.json()["id"]

  def testNewUserReadBook(self):
    testBooks.append({"ISBN": randint(0, randintUpperLimit), "title": uuid.uuid1().hex, "author": uuid.uuid1().hex})
    response = requests.post(applicationLayerDomain + "Books", json={"ISBN": testBooks[-1]["ISBN"], "title": testBooks[-1]["title"], "author": testBooks[-1]["author"]}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    testBooks[-1]["id"] = response.json()["id"]
    testUserReadBooks.append({"userId": testUsers[-1]["id"], "bookId": testBooks[-1]["id"], "favourite": 0})
    response = requests.post(applicationLayerDomain + "UserReadBooks", json=testUserReadBooks[-1], auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    testUserReadBooks[-1]["id"] = response.json()["id"]
    assert response, "Could not create UserReadBook SERVER RESPONSE=" + str(response)

  def testCreateUserReadBookWithNotEnoughDetails(self):
    response = requests.post(applicationLayerDomain + "UserReadBooks", json={"userId": "doesn't matter"}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response.status_code == 400, "POST should have responded with a 400 code to say there is not enough data to make a new UserReadBook SERVER RESPONSE=" + str(response)

  def testGetAllUserReadBooks(self):
    testBooks.append({"ISBN": randint(0, randintUpperLimit), "title": uuid.uuid1().hex, "author": uuid.uuid1().hex})
    response = requests.post(applicationLayerDomain + "Books", json={"ISBN": testBooks[-1]["ISBN"], "title": testBooks[-1]["title"], "author": testBooks[-1]["author"]}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    testBooks[-1]["id"] = response.json()["id"]
    if not testUserReadBooks:
      testUserReadBooks.append({"userId": testUsers[-1]["id"], "bookId": testBooks[-1]["id"], "favourite": 0})
      response = requests.post(applicationLayerDomain + "UserReadBooks", json=testUserReadBooks[-1], auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
      testUserReadBooks[-1]["id"] = response.json()["id"]

    response = requests.get(applicationLayerDomain + "UserReadBooks", auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response and response.json(), "No UserReadBooks retrieved SERVER RESPONSE=" + str(response)
    userReadBookFound = False
    for userReadBook in response.json():
      if userReadBook["id"] == testUserReadBooks[-1]["id"]:
        userReadBookFound = True
    assert userReadBookFound, "Can't find recently created UserReadBook in list of all UserReadBooks SERVER RESPONSE=" + str(response)

class UserReadBookTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if not testUsers:
      testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
      testUsers[-1]["id"] = response.json()["id"]
    if not testBooks:
      testBooks.append({"ISBN": randint(0, randintUpperLimit), "title": uuid.uuid1().hex, "author": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Books", json={"ISBN": testBooks[-1]["ISBN"], "title": testBooks[-1]["title"], "author": testBooks[-1]["author"]}, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
      testBooks[-1]["id"] = response.json()["id"]
    if not testUserReadBooks:
      testUserReadBooks.append({"userId": testUsers[-1]["id"], "bookId": testBooks[-1]["id"], "favourite": 0})
      response = requests.post(applicationLayerDomain + "UserReadBooks", json=testUserReadBooks[-1], auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
      testUserReadBooks[-1]["id"] = response.json()["id"]
  
  def testGetUserReadBook(self):
    response = requests.get(applicationLayerDomain + "UserReadBooks/" + testUserReadBooks[-1]["id"], auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response, "get request should have returned a UserReadBook SERVER RESPONSE=" + str(response)

  def testGetInvalidUserReadBook(self):
    response = requests.get(applicationLayerDomain + "UserReadBooks/2", auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response.status_code == 404, "get request should not have returned a UserReadBook SERVER RESPONSE=" + str(response)
  
  def testChangingFavourite(self):
    data = {"favourite": 1}
    response = requests.put(applicationLayerDomain + "UserReadBooks/" + testUserReadBooks[-1]["id"], json=data, auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response.status_code == 204, "Server should have changed the favourite value of the UserReadBook SERVER RESPONSE=" + str(response)

class LogsTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    #create a least one log message
    if not testUsers:
      testUsers.append({"username": uuid.uuid1().hex, "password": uuid.uuid1().hex})
      response = requests.post(applicationLayerDomain + "Users", json={"username": testUsers[-1]["username"], "password": testUsers[-1]["password"]})
      testUsers[-1]["id"] = response.json()["id"]

  def testGetAllLogs(self):
    response = requests.get(applicationLayerDomain + "Logs", auth=HTTPBasicAuth(testUsers[-1]["username"], testUsers[-1]["password"]))
    assert response, "get request should have returned several logs SERVER RESPONSE=" + str(response)
  
if __name__ == '__main__':
  unittest.main()