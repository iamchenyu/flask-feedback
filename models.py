from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


# As a convenience, if we run this module interactively, the method below will leave you in a state of being able to work with the database directly.
# So that we can use Flask-SQLAlchemy, we'll make a Flask app
if __name__ == "__main__":
    from app import app
    connect_db(app)


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    feedback = db.relationship(
        "Feedback", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User {self.id} - {self.username}"

    def greet(self):
        return f"Hi! My name is {self.first_name.capitalize()} {self.last_name.capitalize()}.My email address is {self.email}. Feel free to contact me!"

    @classmethod
    def register(cls, **kwargs):
        hashed = bcrypt.generate_password_hash(kwargs["password"])
        hashed_utf8 = hashed.decode("utf8")
        kwargs["password"] = hashed_utf8
        return cls(**kwargs)

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter(cls.username == username).first()
        if not user:
            raise NameError("user not found")
        elif user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            raise ValueError("wrong password")


class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"Feedback {self.id} - {self.title} By User {self.user_id}"
