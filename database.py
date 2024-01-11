from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase("database.db")
daysNames = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


class Classroom(Model):
    number = TextField(default="")  # используем здесь строку, так как в будещем возможны такие кабинеты как 1А и т.п.
    capacity = IntegerField(default=0)

    class Meta:
        database = db
        db_table = "Classroom"


class Lessons(Model):
    name = TextField(default="")
    classroom = ForeignKeyField(Classroom, to_field="number")
    dayWeak = IntegerField(default=1)  # день недели, где 1 - понедельник, 7 - воскресенье
    hidden = BooleanField(default=False)

    class Meta:
        database = db
        db_table = "Lessons"


class Teachers(Model):
    name = TextField(default="")
    hidden = BooleanField(default=False)

    class Meta:
        database = db
        db_table = "Teachers"


class TeachLessons(Model):  # для создания связи многие ко многим необходима третья таблица
    teacher = ForeignKeyField(Teachers, to_field="id")
    lesson = ForeignKeyField(Lessons, to_field="id")

    class Meta:
        database = db
        db_table = "TeachLessons"


def connect():
    db.connect()
    Classroom.create_table()
    Lessons.create_table()
    Teachers.create_table()
    TeachLessons.create_table()
