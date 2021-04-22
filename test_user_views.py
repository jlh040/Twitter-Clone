"""User View tests."""

# Set the database url before we import app
os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app, CURR_USER_KEY
from models import db, connect_db, User, Message
from unittest import TestCase
import os

app.config['WTF_CSRF_ENABLED'] = True
app.config['TESTING'] = True

class UserViewTestCase(TestCase):
    """Test the user related routes."""

    def setUp(self):
        """Clear the database, make a user, and set up the test client."""

        User.query.delete()
        Message.query.delete()

        self.testuser = User.signup(
            username="some_username",
            email="bob74@gmail.com",
            password="thisismypass1",
            image_url=None
        )
        db.session.commit()

        self.client = app.test_client()
    
    def test_see_followers_logged_in(self):
        """Can you see followers of other users when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # Make another user
            user2 = User.signup(
                username='diesel11',
                email="abc@gmail.com",
                password="truck",
                image_url="random.jpg"
            )

            # Re-add user to session
            db.session.add(self.testuser)

            # Follow this user
            self.testuser.following.append(user2)
            db.session.commit()
            
            # Check the status code
            resp = c.get(f'/users/{user2.id}/followers')
            self.assertEqual(resp.status_code, 200)

            # Check that you can see this user's followers
            resp2 = c.get(f'/users/{user2.id}/followers')
            html = resp2.get_data(as_text=True)
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)
    
    def test_see_following_logged_in(self):
        """Can you see who a user is following when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # Make another user
            user2 = User.signup(
                username='diesel11',
                email="abc@gmail.com",
                password="truck",
                image_url="random.jpg"
            )

            # Re-add user to session
            db.session.add(self.testuser)
            
            # Have this user follow you
            self.testuser.followers.append(user2)
            db.session.commit()
            
            # Check the status code
            resp = c.get(f'/users/{user2.id}/following')
            self.assertEqual(resp.status_code, 200)

            # Check that you can see who this user is following
            resp2 = c.get(f'/users/{user2.id}/following')
            html = resp2.get_data(as_text=True)
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)
    
    def test_see_followers_nli(self):
        """Are you prohibited from seeing a user's followers when not logged in?"""

        with self.client as c:
            random_id = 17
            resp = c.get(f'/users/{random_id}/followers')

            # Do we get redirected?
            self.assertEqual(resp.status_code, 302)

            # Do we see the unauthorized message?
            resp2 = c.get(f'/users/{random_id}/followers', follow_redirects=True)
            html = resp2.get_data(as_text=True)
            self.assertIn('Access unauthorized', html)
    
    def test_see_following_nli(self):
        """Are you prohibited from seeing who a user is following when not logged in?"""

        with self.client as c:
            random_id = 673
            resp = c.get(f'/users/{random_id}/following')

            # Are we redirected?
            self.assertEqual(resp.status_code, 302)

            # Do we see the unauthorized message?
            resp2 = c.get(f'/users/{random_id}/following', follow_redirects=True)
            html = resp2.get_data(as_text=True)
            self.assertIn('Access unauthorized', html)

