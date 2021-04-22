"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test functionality for the user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_defaults(self):
        """Do our default values show up?"""

        user = User(
            username="some_guy11",
            email="abc123@gmail.com",
            password="blub55"
        )

        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.image_url, '/static/images/default-pic.png')
        self.assertEqual(user.header_image_url, '/static/images/warbler-hero.jpg')
        self.assertEqual(user.bio, None)
        self.assertEqual(user.location, None)
    
    def test_repr(self):
        """Does the repr method return a representation of a user?"""

        user = User(
            username="mike11",
            email="someguy44@mail.com",
            password="1234k"
        )
        db.session.add(user)
        db.session.commit()

        self.assertEqual(str(user), f'<User #{user.id}: {user.username}, {user.email}>')