from bucketlist import app
import unittest
from bucketlist.models import db, User


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        """ Default configuration. """
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../testbucketlist.db"
        app.config["TESTING"] = True
        """ Update to use fixtures instead """
        db.drop_all()
        db.create_all()  # create all tables based
        new_user = User(username="admin", password="admin")
        db.session.add(new_user)
        db.session.commit()  # user is now in our database
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()  # will call session remove
        db.drop_all()


if __name__ == "main":
    unittest.main()
