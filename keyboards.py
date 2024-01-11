from telebot import types

menuMain = types.InlineKeyboardMarkup()
menuMain.add(
    types.InlineKeyboardButton(text="Предметы", callback_data="openLessons"),
    types.InlineKeyboardButton(text="Преподы", callback_data="openTeachers")
).add(
    types.InlineKeyboardButton(text="Расписание", callback_data="openSchedule")
)

cancelReply = types.ReplyKeyboardMarkup(True)
cancelReply.add("Отмена")

remove = types.ReplyKeyboardRemove()

backMenu = types.InlineKeyboardMarkup()
backMenu.add(
    types.InlineKeyboardButton(text="Вернуться в меню.", callback_data="openMenu")
)
