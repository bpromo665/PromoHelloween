import os

from project import bot, session
from telebot import types
import config
import project.modules.start as start
import xlrd
from project.models import PromoCode, User
import project.modules.general as general


def get_user(username=None, telegram_id=None):
    try:
        if telegram_id is not None:
            return session.query(User).filter_by(telegram_id=str(telegram_id)).first()
        elif username is not None:
            return session.query(User).filter_by(username=username).first()
    except Exception as e:
        print(e)
        return None


def handle_admin(message: types.Message):

    user = get_user(telegram_id=message.from_user.id)

    if user is not None and user.is_admin:
        markup = types.ReplyKeyboardMarkup(True, True)

        button1 = types.KeyboardButton('Додати промо коди')
        button2 = types.KeyboardButton('Додати товари')
        button3 = types.KeyboardButton('Додати адміністратора')
        button4 = types.KeyboardButton('Видалити адміністратора')

        markup.row(button1, button2)
        markup.row(button3, button4)

        bot.send_message(message.chat.id, "Оберіть потрібну функцію:", reply_markup=markup)
        bot.register_next_step_handler(message, menu_handler)
    else:
        start.handle_start(message)


def menu_handler(message: types.Message):
    if message.text == 'Додати промо коди':
        bot.send_message(message.chat.id, "Відправте мені файл у форматі .xlsx")
        bot.register_next_step_handler(message, add_promo_code)
    elif message.text == 'Додати товари':
        bot.send_message(message.chat.id, "Відправте мені файл у форматі .xlsx")
        bot.register_next_step_handler(message, add_promo_items)

    elif message.text == 'Додати адміністратора':
        bot.send_message(message.chat.id, "Надашліть мені юзернейм БЕЗ @")
        bot.register_next_step_handler(message, add_admin)

    elif message.text == 'Видалити адміністратора':
        bot.send_message(message.chat.id, "Надашліть мені юзернейм БЕЗ @")
        bot.register_next_step_handler(message, remove_admin)

    elif message.text == '/start':
        start.handle_start(message)

    else:
        handle_admin(message)


def add_admin(message):
    try:
        user = get_user(username=str(message.text))
        user.is_admin = True
        session.commit()
        bot.send_message(message.chat.id, f"Успішно додали админістратора\n {user}")
    except Exception as e:
        bot.send_message(message.chat.id, e)
    finally:
        menu_handler(message)


def remove_admin(message):
    try:
        user = get_user(username=str(message.text))
        user.is_admin = False
        session.commit()
        bot.send_message(message.chat.id, f"Успішно видалили админістратора\n {user}")
    except Exception as e:
        bot.send_message(message.chat.id, e)
    finally:
        menu_handler(message)


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
        bot.send_message(message.chat.id, 'Схоже що дані були успішно додані до базі даних!')
    except Exception as e:
        bot.send_message(message.chat.id, e)
    finally:
        menu_handler(message)


@bot.message_handler(content_types=['document'])
def add_promo_items(message: types.Message):
    file_path = './Товары.xlsx'
    try:
        file = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file.file_path)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        workbook = xlrd.open_workbook("Товары.xlsx")
        worksheet = workbook.sheet_by_index(0)

        codes = session.query(PromoCode).filter_by(prize=None).all()

        iter = 0

        for i in range(0, worksheet.nrows):
            for j in range(0, worksheet.ncols):
                if j == 1:
                    for k in range(0, int(worksheet.cell_value(i, 1))):
                        codes[iter].prize = worksheet.cell_value(i, 0)
                        iter += 1
        bot.send_message(message.chat.id, 'Будь ласка зачекайте, ми завантажуємо дані...')
        session.commit()
        bot.send_message(message.chat.id, 'Схоже що дані були успішно додані до базі даних!')
    except Exception as e:
        bot.send_message(message.chat.id, e)
    finally:
        menu_handler(message)