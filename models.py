from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Entry(db.Model):
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(150), nullable=False)
    sink = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # Store '🛠️ Necessity'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship for querying user details
    user = db.relationship('User', backref='entries', lazy=True)

    def __repr__(self):
        return f"Entry('{self.source}', '{self.sink}', '{self.type}')"