from project import bot
from telebot import types
import config
import project.modules.start as start
import xlrd


def handle_admin(message: types.Message):
    if message.from_user.username is config.ADMIN_USERNAME:
        markup = types.ReplyKeyboardMarkup(True, True)

        button1 = types.KeyboardButton('Додати промо коди')
        button2 = types.KeyboardButton('Додати товари')

        markup.row(button1)
        markup.row(button2)
        bot.send_message(message.chat.id, "Оберіть потрібну функцію:", reply_markup=markup)
    else:
        start.handle_start(message)


def menu_handler(message: types.Message):
    if message.text == 'Додати промо коди':
        bot.send_message(message.chat.id, "Відправте мені файл у форматі .xlsx")
        bot.register_next_step_handler(message, add_promo_code)
    elif message.text == 'Додати товари':
        pass
    else:
        handle_admin(message)


@bot.message_handler(content_types=['document'])
def add_promo_code(message: types.Message):
    file = bot.get_file(message.document.file_id)
    workboot = xlrd.open_workbook(file)
    worksheet = workbook.sheet_by_index(0)
    for i in range(0, 5):
        for j in range(0, 3):
            print(worksheet.cell_value(i, j), end='\t')
        print('')