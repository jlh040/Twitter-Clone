"""Message model tests."""

import os
from unittest import TestCase
from models import db, User, Message

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

class MessageModelTestCase(TestCase):
    """Test functionality for the message model."""

    def setUp(self):
        """Delete any leftover sample data."""
        
        User.query.delete()
        Message.query.delete()
    
    def tearDown():
        """Clear the session."""
        db.session.rollback()
    
    