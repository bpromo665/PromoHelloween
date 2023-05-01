import os

from project import bot, session
from telebot import types
import config
import project.modules.start as start
import xlrd
from project.models import PromoCode
import project.modules.general as general


def handle_admin(message: types.Message):
    if message.from_user.username == config.ADMIN_USERNAME:
        markup = types.ReplyKeyboardMarkup(True, True)

        button1 = types.KeyboardButton('Додати промо коди')
        button2 = types.KeyboardButton('Додати товари')

        markup.row(button1)
        markup.row(button2)
        bot.send_message(message.chat.id, "Оберіть потрібну функцію:", reply_markup=markup)
        bot.register_next_step_handler(message, menu_handler)
    else:
        start.handle_start(message)


def menu_handler(message: types.Message):
    if message.text == 'Додати промо коди':
        bot.send_message(message.chat.id, "Відправте мені файл у форматі .xlsx")
        bot.register_next_step_handler(message, add_promo_code)
    elif message.text == 'Додати товари':
        pass

    elif message.text == '/start':
        start.handle_start(message)

    elif message.text == '/admin':
        handle_admin(message)

    else:
        handle_admin(message)


@bot.message_handler(content_types=['document'])
def add_promo_code(message: types.Message):
    file_path = './Коды.xlsx'
    try:
        file = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file.file_path)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        workbook = xlrd.open_workbook("Коды.xlsx")
        worksheet = workbook.sheet_by_index(0)

        for i in range(0, worksheet.nrows):
            for j in range(0, worksheet.ncols):
                session.add(PromoCode(code=worksheet.cell_value(i, j)))
        session.commit()
    except Exception as e:
        bot.send_message(message.chat.id, e)
    finally:
        try:
            os.remove('Коды.xlsx')

        except Exception as e:
            print(e)

        menu_handler(message)
