import datetime

from telebot import TeleBot
from keyboards import *
from config import *
from database import *

bot = TeleBot(token)
connect()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, выбери функцию.', reply_markup=menuMain)


@bot.callback_query_handler(func=lambda call: call.data == "openSchedule")
def openSchedule(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    text = "Расписание:\n\n"
    for day in range(1, 8):
        text += "\n" + daysNames[day - 1] + "\n"
        lessonsDay = Lessons.select().where((Lessons.hidden == False) & (Lessons.dayWeak == day))
        if not lessonsDay:
            text += "В этот день занятий нет.\n"
            continue
        for lesson in lessonsDay:
            text += f"Предмет {lesson.name}, проходит в кабинете №{lesson.classroom.number} с вместимостью {lesson.classroom.capacity}\n"
            teachers = [i.teacher for i in TeachLessons.select().where(TeachLessons.lesson == lesson)]
            teachers = [i.name for i in teachers if not i.hidden]
            text += f"Ведёт {len(teachers)} преподавателей.\n"
            if teachers:
                text += "\n".join(teachers) + "\n"
    today = datetime.datetime.now().weekday()
    text += f"\nСегодня {daysNames[today].lower()}!"
    bot.send_message(call.message.chat.id, text, reply_markup=backMenu)


@bot.callback_query_handler(func=lambda call: call.data == "openLessons")
def openLessons(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    lessons = Lessons.select().where(Lessons.hidden == False)[::-1]  # переворачиваем список, дабы новые записи появлялись сверху
    kb = types.InlineKeyboardMarkup()
    for i in range(len(lessons) // 2):
        kb.add(
            types.InlineKeyboardButton(text=lessons[i * 2].name, callback_data=f"viewLesson {lessons[i * 2].id}"),
            types.InlineKeyboardButton(text=lessons[i * 2 + 1].name, callback_data=f"viewLesson {lessons[i * 2 + 1].id}")
        )
    if len(lessons) % 2 == 1:
        kb.add(
            types.InlineKeyboardButton(text=lessons[-1].name, callback_data=f"viewLesson {lessons[-1]}")
        )
    kb.add(
        types.InlineKeyboardButton(text="Добавить", callback_data="addLesson"),
        types.InlineKeyboardButton(text="Назад", callback_data="openMenu")
    )
    bot.send_message(call.message.chat.id, "Выберите нужный предмет/добавьте новый.", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == "openTeachers")
def openTeachers(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    teachers = Teachers.select().where(Teachers.hidden == False)[::-1]
    kb = types.InlineKeyboardMarkup()
    for i in range(len(teachers) // 2):
        kb.add(
            types.InlineKeyboardButton(text=teachers[i * 2].name, callback_data=f"viewTeacher {teachers[i * 2].id}"),
            types.InlineKeyboardButton(text=teachers[i * 2 + 1].name,
                                       callback_data=f"viewTeacher {teachers[i * 2 + 1].id}")
        )
    if len(teachers) % 2 == 1:
        kb.add(
            types.InlineKeyboardButton(text=teachers[-1].name, callback_data=f"viewTeacher {teachers[-1]}")
        )
    kb.add(
        types.InlineKeyboardButton(text="Добавить", callback_data="addTeacher"),
        types.InlineKeyboardButton(text="Назад", callback_data="openMenu")
    )
    bot.send_message(call.message.chat.id, "Выберите нужного препода.", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == "addTeacher")
def addTeacher(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Введите имя преподавателя", reply_markup=cancelReply)
    bot.register_next_step_handler(call.message, addTeacherStep1)


@bot.callback_query_handler(func=lambda call: call.data == "addLesson")
def addLesson(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Введите название предмета", reply_markup=cancelReply)
    bot.register_next_step_handler(call.message, createLessonStep1)


@bot.callback_query_handler(func=lambda call: call.data.startswith("viewTeacher"))
def viewTeacher(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    teacher_id = int(call.data.split()[1])
    teacher = Teachers.select().where(Teachers.id == teacher_id)[0]
    lessons = [lesson.lesson for lesson in TeachLessons.select().where((TeachLessons.teacher == teacher))]
    lessons = [lesson.name for lesson in lessons if not lesson.hidden]
    l = "\n".join(lessons)
    text = f"Преподаватель {teacher.name} ведёт {len(lessons)} занятий:\n{l}\n\nВыберите действие"
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text="Удалить", callback_data=f"deleteTeacher {teacher_id}")
    ).add(
        types.InlineKeyboardButton(text="Назад", callback_data="openTeachers")
    )
    bot.send_message(call.message.chat.id, text, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("deleteTeacher"))
def deleteTeacher(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    Teachers.update(hidden=True).where(Teachers.id == int(call.data.split()[1])).execute()
    bot.send_message(call.message.chat.id, "Преподаватель успешно удалён!", reply_markup=backMenu)


@bot.callback_query_handler(func=lambda call: call.data.startswith("deleteLesson"))
def deleteLesson(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    Lessons.update(hidden=True).where(Lessons.id == int(call.data.split()[1])).execute()
    bot.send_message(call.message.chat.id, "Предмет успешно удалён!", reply_markup=backMenu)


@bot.callback_query_handler(func=lambda call: call.data.startswith("viewLesson"))
def viewLesson(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    lesson_id = int(call.data.split()[1])
    lesson = Lessons.select().where(Lessons.id == lesson_id)[0]
    teachers = TeachLessons.select().where(TeachLessons.lesson == lesson)
    text = f"Предмет {lesson.name}\nКабинет: {lesson.classroom}\nВместимость: {lesson.classroom.capacity}\nКол-во преподавателей: {len(teachers)}\n"
    text += f"\n".join([teacher.teacher.name for teacher in teachers])
    text += "\nВыберите действие"
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text="Удалить", callback_data=f"deleteLesson {lesson_id}")
    ).add(
        types.InlineKeyboardButton(text="Назад", callback_data="openLessons")
    )
    bot.send_message(call.message.chat.id, text, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == "openMenu")
def openMenu(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Привет, выбери функцию.", reply_markup=menuMain)


def addTeacherStep1(message):
    if not message.text or message.text == "Отмена":
        bot.send_message(message.chat.id, "Добавление отменено.", reply_markup=remove)
        return bot.send_message(message.chat.id, "Возвращаюсь в меню.", reply_markup=menuMain)
    Teachers.create(name=message.text)
    bot.send_message(message.chat.id, "Преподаватель добавлен.", reply_markup=remove)
    bot.send_message(message.chat.id, "Выбери функцию.", reply_markup=menuMain)


def createLessonStep1(message):
    if not message.text or message.text == "Отмена":
        bot.send_message(message.chat.id, "Добавление отменено.", reply_markup=remove)
        return bot.send_message(message.chat.id, "Привет, выбери функцию.", reply_markup=menuMain)
    name = message.text
    bot.send_message(message.chat.id, "Введите номер кабинета (от 1 до 150)", reply_markup=cancelReply)
    bot.register_next_step_handler(message, createLessonStep2, name)


def createLessonStep2(message, name):
    if not message.text or not Classroom.select().where(Classroom.number == message.text).exists():
        bot.send_message(message.chat.id, "Добавление отменено.", reply_markup=remove)
        return bot.send_message(message.chat.id, "Привет, выбери функцию.", reply_markup=menuMain)
    classroom = Classroom.select().where(Classroom.number == message.text)[0]
    lesson = Lessons.create(name=name, classroom=classroom)
    bot.send_message(message.chat.id, 'Впишите день недели, по которым преподаётся этот предмет\nПример: "1", "2", "4"', reply_markup=cancelReply)
    bot.register_next_step_handler(message, createLessonStep3, lesson)


def createLessonStep3(message, lesson):
    if not message.text or not message.text.isdigit() or 1 > int(message.text) > 7:
        lesson.delete_instance()
        bot.send_message(message.chat.id, "Добавление отменено.", reply_markup=remove)
        return bot.send_message(message.chat.id, "Привет, выбери функцию.", reply_markup=menuMain)
    Lessons.update(dayWeak=int(message.text)).where(Lessons.id == lesson.id).execute()
    teachers = Teachers.select().where(Teachers.hidden == False)
    text = "Список преподавателей:\n"
    for teacher in teachers:
        text += f"\n{teacher.id} - {teacher.name}"
    text += "\n\nВведите номера преподавателей через пробел или напишите 0"
    bot.send_message(message.chat.id, text, reply_markup=cancelReply)
    bot.register_next_step_handler(message, createLessonStep4, lesson)


def createLessonStep4(message, lesson):
    if not message.text or message.text == "Отмена":
        lesson.delete_instance()
        bot.send_message(message.chat.id, "Добавление отменено.", reply_markup=remove)
        return bot.send_message(message.chat.id, "Привет, выбери функцию.", reply_markup=menuMain)
    teachers_ids = list(map(int, message.text.split(" ")))
    for teacher_id in teachers_ids:
        if Teachers.select().where(Teachers.id == teacher_id).exists():
            teacher = Teachers.select().where(Teachers.id == teacher_id)[0]
            TeachLessons.create(lesson=lesson, teacher=teacher)
    bot.send_message(message.chat.id, "Предмет успешно создан!", reply_markup=remove)
    bot.send_message(message.chat.id, 'Выбери функцию.', reply_markup=menuMain)


if __name__ == "__main__":
    bot.infinity_polling()
