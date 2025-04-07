from peewee import *
from config import *
import datetime

db = SqliteDatabase('db.sqlite3')


class BaseModel(Model):

    class Meta:
        database = db


class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)


class Message(BaseModel):
    id = BigIntegerField(primary_key=True)
    from_user = ForeignKeyField(User, backref='messages')
    text = TextField(null=True)
    date = DateTimeField(default=datetime.datetime.now)
    is_bot = BooleanField(default=False)
    reply_to = ForeignKeyField('self', null=True)


class Permission(BaseModel):
    user = ForeignKeyField(User, backref='permissions')
    status = IntegerField(default=0)  # 0=عادی, 1=ویژه, 2=ادمین, 3=مالک


class GeminiUsage(BaseModel):
    user = ForeignKeyField(User, on_delete="CASCADE")
    date = DateField(default=datetime.date.today)
    count = IntegerField(default=0)


class BotStatus(BaseModel):
    is_active = BooleanField(default=True)


def create_tables():
    with db:
        db.create_tables([User, Message, Permission, BotStatus, GeminiUsage])
