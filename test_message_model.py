"""Message model tests."""

import os
from unittest import TestCase
from models import db, User, Message
from datetime import datetime

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
    
    def tearDown(self):
        """Clear the session."""
        db.session.rollback()
    
    def test_message_model(self):
        """Does basic message model work?"""

        user = User.signup(
            username="bob_dango",
            password="dosmespa11",
            email="dsfkk@gmail.com",
            image_url=None
        )
        db.session.add(user)
        db.session.commit()

        message = Message(
            text="This is some nice text",
            user_id=user.id
        )

        db.session.add(message)
        db.session.commit()

        # Do we have access to the attributes?
        self.assertIsInstance(message.text, str)
        self.assertIsInstance(message.user_id, int)
        self.assertIsInstance(message.timestamp, datetime)

        # Do we have access to the user?
        user = User.query.filter(User.id == user.id).one()
        self.assertIs(user, message.user)
    