"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError, InvalidRequestError

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
    
    def tearDown(self):
        db.session.rollback()
    

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
    
    def test_is_following(self):
        """Does is_following detect when a user follows another user?"""

        user1 = User(
            username="user1",
            email="hotwow@mail.com",
            password="bub1"
        )

        user2 = User(
            username="user2",
            email="wowbot@mail.com",
            password="fraek"
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        user1.followers.append(user2)

        self.assertTrue(user2.is_following(user1))

    def test_is_not_following(self):
        """Does is_following work when a user is not following another user?"""

        user1 = User(
            username="user1",
            email="hotwow@mail.com",
            password="bub1"
        )

        user2 = User(
            username="user2",
            email="wowbot@mail.com",
            password="fraek"
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        self.assertFalse(user2.is_following(user1))
    
    def test_is_followed_by(self):
        """Does is_followed_by detect when a user is followed by another user?"""

        user1 = User(
            username="user1",
            email="hotwow@mail.com",
            password="bub1"
        )

        user2 = User(
            username="user2",
            email="wowbot@mail.com",
            password="fraek"
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        user1.followers.append(user2)

        self.assertTrue(user1.is_followed_by(user2))

    def test_is_not_followed_by(self):
        """Does is_followed_by detect when a user is not followed by another user?"""

        user1 = User(
            username="user1",
            email="hotwow@mail.com",
            password="bub1"
        )

        user2 = User(
            username="user2",
            email="wowbot@mail.com",
            password="fraek"
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        self.assertFalse(user1.is_followed_by(user2))
    
    def test_sign_up(self):
        """Does signup successfully create a user if their credentials are valid?"""

        user_1 = User.signup(
            username="billybob",
            password="thornton",
            email="badnewsbears@mail.com",
            image_url=None
        )

        self.assertTrue(user_1)
    
    def test_signup_invalid_creds(self):
        """Does signup fail to create a user if any validations fail?"""

        user_1 = User.signup(
            username="Some_guy_some_where234",
            password="whoami",
            email="badnewsbears@lipwip.com",
            image_url=None
        )

        user_2 = User.signup(
            username="Some_guy_some_where234",
            password="thisisanewone",
            email="whydo@gmail.com",
            image_url=None
        )

        # Does a duplicate username cause a failure?
        try:
            db.session.add_all([user_1, user_2])
            db.session.commit()
        except IntegrityError as err:
            self.assertIsInstance(err, IntegrityError)
        
        # Do empty fields cause a failure?
        try:
            user_3 = User.signup(username="hello56")
        except TypeError as err:
            self.assertIsInstance(err, TypeError)
    
    def test_user_authenticate_success(self):
        """Does authenticate successfully return a user given valid credentials?"""

        user1 = User.signup(
            username="bobby",
            password="robby7673",
            email="some_guy87@gmail.com",
            image_url=None
        )
        db.session.add(user1)
        db.session.commit()

        self.assertEqual(user1.authenticate(username='bobby', password='robby7673'), user1)
        




        