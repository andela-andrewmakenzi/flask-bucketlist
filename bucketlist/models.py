from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from passlib.hash import sha256_crypt
from . import app


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./bucketlist.db"
db = SQLAlchemy(app)


class Bucketlist(db.Model):

    __tablename__ = "Bucketlist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    """ You can set this so it changes whenever the row is updated """
    date_modified = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, nullable=False)
    """ creates an association in Items so we can get the
    bucketlist an item belongs to """
    items = db.relationship("Items", backref="bucket", lazy="dynamic")

    def __init__(self, name, date_created, created_by, date_modified):
        self.name = name
        self.date_created = date_created
        self.created_by = created_by
        self.date_modified = date_modified

    def __repr__(self):
        return "<{} {} {} {} {} >".format(self.id, self.name, self.date_created, self.date_modified, self.created_by)

    def set_last_modified_date(self, date):
        self.date_modified = date

    def returnthis(self):
        allitems = [item.returnthis() for item in self.items]
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
            "created_by": self.created_by,
            "items": allitems
        }


class Items(db.Model):

    __tablename__ = "Items"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    """ You can set this so that it changes whenever the row is updated """
    date_modified = db.Column(db.DateTime, nullable=True)
    done = db.Column(db.Boolean, nullable=False, unique=False, default=False)
    bucketlistid = db.Column(db.Integer, db.ForeignKey("Bucketlist.id"), nullable=False, unique=False)

    def __init__(self, name, date_created, date_modified, bucketlistid, done=False):
        self.name = name
        self.date_created = date_created
        self.done = done
        self.date_modified = date_modified
        self.bucketlistid = bucketlistid

    def __repr__(self):
        return "<{} {} {} {} {} >".format(self.userid, self.name, self.date_created, self.date_modified, self.done)

    def set_last_modified_date(self, date):
        self.date_modified = date

    def returnthis(self):
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
            "done": self.done
        }


class User(db.Model):

    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = self.hash_password(password)

    def __repr__(self):
        return "<{} {} {}>".format(self.id, self.username, self.password)

    def validate_password(self, supplied_password):
        """ validate if password supplied is correct """
        return sha256_crypt.verify(supplied_password, self.password)

    def hash_password(self, password):
        return sha256_crypt.encrypt(password)

    def generate_auth_token(self):
        # generate authentication token based on the unique userid field
        s = Serializer(app.config['SECRET_KEY'], expires_in=6000)
        return s.dumps({"id": self.id})  # this is going to be binary

    @staticmethod
    # this is static as it is called before the user object is created
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'], expires_in=6000)
        try:
            # this should return the user id
            user = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        return user["id"]
