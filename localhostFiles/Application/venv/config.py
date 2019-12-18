WTF_CSRF_ENABLED = True
SECRET_KEY = b'R$\xb1\x07o)\xafV\xb6\xab\x1b0\xd9\xac3\x9f\xfd\xb1s\x9cb\x02:@'

import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True  