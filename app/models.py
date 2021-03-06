# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app import db, bc
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    hashed_password = db.Column(db.Binary(60), nullable=False)

    def __init__(self, user, email, password):
        self.user = user
        self.hashed_password = bc.generate_password_hash(password)
        self.email = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def is_correct_password(self, password):
        return bc.check_password_hash(self.hashed_password, password)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self
