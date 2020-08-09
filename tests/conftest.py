import pytest
import os

from app.models import User
from app import app
from sqlalchemy.orm import scoped_session, sessionmaker
session = scoped_session(sessionmaker())

basedir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='module')
def new_user():
    user = User('staff1', 'staff1@gmail.com', 'testingpassword')
    return user


@pytest.yield_fixture(scope='session')
def client():
    test_client = app.test_client()
    return test_client
