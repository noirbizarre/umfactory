import pytest

from umongo import MotorAsyncIOInstance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient

from umfactory import Factory

from conftest import DB_URI

pytestmark = pytest.mark.asyncio

instance = MotorAsyncIOInstance()


@instance.register
class Person(Document):
    name = fields.StringField(required=True)
    age = fields.IntegerField(required=True)
    surname = fields.StringField()


class PersonFactory(Factory):
    class Meta:
        model = Person


@pytest.fixture
def client(event_loop):
    return AsyncIOMotorClient(DB_URI, io_loop=event_loop)


@pytest.fixture(autouse=True)
def db(client):
    db = client.get_database()
    instance.init(db)
    return db


async def test_without_params():
    person = await PersonFactory.create()
    assert isinstance(person.name, str)
    assert isinstance(person.age, int)
    assert person.surname is None


async def test_with_params():
    person = await PersonFactory.create(age=5, surname='fake')
    assert isinstance(person.name, str)
    assert person.age == 5
    assert person.surname == 'fake'
