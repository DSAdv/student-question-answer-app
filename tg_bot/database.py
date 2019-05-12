import logging
from datetime import datetime
from functools import wraps

import peewee
from telebot import types

import tg_bot.tg_config as config

logger = logging.getLogger("tg::database")
sqlite_db = peewee.SqliteDatabase(config.DATABASE)


def connect_to_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sqlite_db.connect()
        result = func(*args, **kwargs)
        sqlite_db.close()
        return result
    return wrapper


# Model
class BaseModel(peewee.Model):
    class Meta:
        database = sqlite_db


class Group(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    group_id = peewee.IntegerField(index=True, unique=True)
    group_name = peewee.CharField(null=True)
    group_okr = peewee.CharField(default="daily")
    group_type = peewee.CharField(default="bachelor")

    @staticmethod
    def update_data(**kwargs):
        try:
            with sqlite_db.atomic():
                group = Group.create(**kwargs)
                group.save()
        except peewee.IntegrityError as e:
            group = Group.get(Group.group_id == kwargs.get("group_id"))

        return group


class TelegramUser(BaseModel):

    id = peewee.IntegerField(primary_key=True)
    user_id = peewee.IntegerField(unique=True, index=True)

    username = peewee.CharField(unique=True, index=True)
    first_name = peewee.CharField(null=True)
    last_name = peewee.CharField(null=True)

    is_bot = peewee.BooleanField(default=False)

    join_date = peewee.DateTimeField(default=datetime.now())
    last_update_date = peewee.DateTimeField(default=datetime.now())

    group = peewee.ForeignKeyField(Group,
                                   backref="users",
                                   lazy_load=False,
                                   null=True,
                                   default=None)

    @staticmethod
    def update_data(msg: types.Message):
        user_data = {
            "user_id": msg.from_user.id,
            "first_name": msg.from_user.first_name,
            "second_name": msg.from_user.last_name or "",
            "username": msg.from_user.username,
        }

        try:
            with sqlite_db.atomic():
                user = TelegramUser.create(**user_data)
                user.save()
        except peewee.IntegrityError as e:
            print(e)
            user = TelegramUser.find_by_id(user_data["user_id"])
            user.last_update_date = datetime.now()
            user.save()

        return user


    @staticmethod
    def find_by_id(id_):
        user = TelegramUser.get(TelegramUser.user_id == id_)
        return user

    def __str__(self):
        return "<TelegramUser [{user_id}]>\nCreated at: {date}".format(
            user_id=self.user_id,
            date=self.join_date,
        )

    def __repr__(self):
        return str(self)


models = [Group, TelegramUser]


@connect_to_db
def update_tables(models):
    sqlite_db.create_tables(models, safe=True)


if __name__ == '__main__':
    update_tables(models)