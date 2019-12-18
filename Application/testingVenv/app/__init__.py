from flask import Flask
import unittest

app = Flask(__name__)
app.config.from_object("config")

from app import tests