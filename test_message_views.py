"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase


from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY, do_logout

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

# Let Flask errors be real errors, not HTML pages with error info
app.config['Testing'] = True


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can the user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

            # Make sure the post shows up on our website
            resp2 = c.get('/')
            html = resp2.get_data(as_text=True)
            self.assertIn('<p>Hello</p>', html)
    
    def test_add_message_nli(self):
        """When logged out, is the user prohibited from adding a message?"""

        with self.client as c:
            resp = c.post('/messages/new', data={'text': 'I\'m not logged in'})

            # Are we redirected?
            self.assertEqual(resp.status_code, 302)

            # Are we getting an error message?
            resp2 = c.post('/messages/new', data={'text': 'I\'m not logged in'}, follow_redirects=True)
            html = resp2.get_data(as_text=True)
            self.assertIn('Access unauthorized', html)
    
    def test_delete_message(self):
        """When logged in, can you delete a message."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # Add a message
            resp = c.post('/messages/new', data={'text': 'This is a new message'})

            # Check that the message was added
            self.assertEqual(Message.query.count(), 1)

            # Delete the message
            msg_id = Message.query.first().id
            resp2 = c.post(f'/messages/{msg_id}/delete')

            #Check that the message is gone
            self.assertEqual(Message.query.count(), 0)
    
    def test_delete_message_nli(self):
        """When not logged in, are you prohibited from deleting a message?"""

        with self.client as c:
            random_num = 5
            resp = c.post(f'/messages/{random_num}/delete')

            # Do we get redirected?
            self.assertEqual(resp.status_code, 302)

            # Do we get an error message?
            resp2 = c.post(f'/messages/{random_num}/delete', follow_redirects=True)
            html = resp2.get_data(as_text=True)
            self.assertIn('Access unauthorized', html)
            
    def see_followers_logged_in(self):
        """Can you see followers of other users when logged in?"""
        with self.testclient as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testclient.id
            
            # Make another user
            db.session.commit(User.signup(
                username='diesel11',
                email="abc@gmail.com",
                password="truck",
                image="random.jpg"
            ))
            
            # Follow this user
            user2 = User.query.filter_by(username = 'diesel11')
            self.testuser.following.append(user2)
            db.session.commit()
            
            # Check the status code
            resp = c.get(f'/users/{user2.id}/followers')
            self.assertEqual(resp.status_code, 200)

            # Check that you can see this user's followers
            resp2 = c.get(f'/users/{user2.id}/followers')
            html = resp2.get_data(as_text=True)
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)
    
    def see_following_logged_in(self):
        """Can you see who a user is following when logged in?"""
        with self.testclient as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testclient.id
            
            # Make another user
            db.session.commit(User.signup(
                username='diesel11',
                email="abc@gmail.com",
                password="truck",
                image="random.jpg"
            ))
            
            # Have this user follow you
            user2 = User.query.filter_by(username = 'diesel11')
            self.testuser.followers.append(user2)
            db.session.commit()
            
            # Check the status code
            resp = c.get(f'/users/{user2.id}/following')
            self.assertEqual(resp.status_code, 200)

            # Check that you can see who this user is following
            resp2 = c.get(f'/users/{user2.id}/following')
            html = resp2.get_data(as_text=True)
            self.assertIn(f'<p>@{self.testuser.username}</p>', html)
    
    def see_followers_nli(self):
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
    
    def see_following_nli(self):
        """Are you prohibited from seeing who a user is following when not logged in?"""

        with self.client as c:
            random_id = 673
            resp = c.get(f'/users/{random_id}/following')

            # Are we redirected?
            self.assertEquals(resp.status_code, 302)

            # Do we see the unauthorized message?
            resp2 = c.get(f'/users/{random_id}/following', follow_redirects=True)
            html = resp2.get_data(as_text=True)
            self.assertIn('Access unauthorized', html)


            




