"""User View tests."""

# Set the database url before we import app
os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app, CURR_USER_KEY
from models import db, connect_db, User, Message
from unittest import TestCase
import os

app.config['WTF_CSRF_ENABLED'] = True
app.config['TESTING'] = True



