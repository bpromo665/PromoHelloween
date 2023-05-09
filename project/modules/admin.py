import os

from project import bot, session
from telebot import types

import project.modules.start as start
from project.models import PromoCode, User

import xlrd
import xlwt

from sqlalchemy import desc


def get_user(username=None, telegram_id=None):
    try:
        if telegram_id is not None:
            return session.query(User).filter_by(telegram_id=str(telegram_id)).first()
        elif username is not None:
            return session.query(User).filter_by(username=username).first()
    except Exception as e:
        print(e)
        return None


@bot.message_handler(content_types=['text'])
def handle_admin(message: types.Message):

    user = get_user(telegram_id=message.from_user.id)

    if user is not None and user.is_admin:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        button1 = types.KeyboardButton('Додати промо коди')
        button2 = types.KeyboardButton('Додати товари')
        button3 = types.KeyboardButton('Додати адміністратора')
        button4 = types.KeyboardButton('Видалити адміністратора')
        button5 = types.KeyboardButton('Вивантажити дані')

        markup.row(button1, button2)
        markup.row(button3, button4)
        markup.row(button5)

        bot.send_message(message.chat.id, "Оберіть потрібну функцію:", reply_markup=markup)
        bot.register_next_step_handler(message, menu_handler)
    else:
        start.handle_start(message)


def menu_handler(message: types.Message):
    if message.text == 'Додати промо коди':
        bot.send_message(message.chat.id, "Відправте мені файл у форматі .xlsx\n\n"
                                          "Зауважте! Щоб промо коди правильно завантажились вони повинні мати лише одне поле |Промокод|")
        bot.register_next_step_handler(message, add_promo_code)
    elif message.text == 'Додати товари':
        bot.send_message(message.chat.id, "Відправте мені файл у форматі .xlsx\n\n"
                                          "Зауважте! Щоб товари правильно завантажились вони повинні мати 2 поял |Назва товару| - |Кількість товару|")
        bot.register_next_step_handler(message, add_promo_items)

    elif message.text == 'Додати адміністратора':
        bot.send_message(message.chat.id, "Надашліть мені юзернейм БЕЗ @")
        bot.register_next_step_handler(message, add_admin)

    elif message.text == 'Видалити адміністратора':
        bot.send_message(message.chat.id, "Надашліть мені юзернейм БЕЗ @")
        bot.register_next_step_handler(message, remove_admin)

    elif message.text == 'Вивантажити дані':
        bot.send_message(message.chat.id, "Вивантажуємо дані...")
        get_data(message)

    elif message.text == '/start':
        start.handle_start(message)

    else:
        handle_admin(message)


def get_data(message):
    try:
        users = session.query(User).order_by(desc(User.is_admin)).all()
        codes = session.query(PromoCode).order_by(desc(PromoCode.prize.isnot(None)), desc(PromoCode.is_used)).all()

        create_user_file(users).save("users.xlsx")
        bot.send_document(message.chat.id, open('users.xlsx', 'rb'))

        create_codes_file(codes).save("codes.xlsx")
        bot.send_document(message.chat.id, open('codes.xlsx', 'rb'))

        bot.send_message(message.chat.id, "Успішно!")

    except Exception as e:
        bot.send_message(message.chat.id, e)

    finally:
        message.text = ''
        menu_handler(message)


def create_user_file(data) -> xlwt.Workbook():
    book = xlwt.Workbook()
    sheet = book.add_sheet("Sheet1")

    sheet.write(0, 0, "Ім'я")
    sheet.write(0, 1, "Телеграм id")
    sheet.write(0, 2, "username")
    sheet.write(0, 3, "Номер телефону")
    sheet.write(0, 4, "Адмін")

    for i, user in enumerate(data):
        sheet.write(i + 1, 0, user.id)
        sheet.write(i + 1, 1, user.telegram_id)
        sheet.write(i + 1, 2, user.username)
        sheet.write(i + 1, 3, user.phone_number)
        sheet.write(i + 1, 4, user.is_admin)

    return book


def create_codes_file(data) -> xlwt.Workbook():
    book = xlwt.Workbook()
    sheet = book.add_sheet("Sheet1")

    sheet.write(0, 0, "Код")
    sheet.write(0, 1, "Приз")
    sheet.write(0, 2, "Вже використаний")

    for i, code in enumerate(data):
        sheet.write(i + 1, 0, code.code)
        sheet.write(i + 1, 1, code.prize)
        sheet.write(i + 1, 2, code.is_used)

    return book


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
    print('add_promo_code function')
    try:
        file = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file.file_path)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        workbook = xlrd.open_workbook("Коды.xlsx")
        worksheet = workbook.sheet_by_index(0)

        msg = bot.send_message(message.chat.id, 'Зачекайте, ми завантажуємо дані...')
        promo_codes = []
        for i in range(0, worksheet.nrows):
            if i % 500 == 0:
                bot.edit_message_text(chat_id=message.chat.id, text=f'Завантажили {i} дописів', message_id=msg.id)
                session.bulk_save_objects(promo_codes)
                promo_codes = []
                print('500')
            promo_codes.append(PromoCode(code=worksheet.cell_value(i, 0)))

        session.bulk_save_objects(promo_codes)
        session.commit()
        bot.send_message(message.chat.id, 'Схоже що дані були успішно додані до базі даних!')
    except Exception as e:
        bot.send_message(message.chat.id, e)
        session.rollback()
    finally:
        print('Finaly block')
        os.remove(file_path)
        handle_admin(message)


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
        bot.send_message(message.chat.id, 'Будь ласка зачекайте, ми завантажуємо дані...')
        for i in range(0, worksheet.nrows):
            for j in range(0, worksheet.ncols):
                if j == 1:
                    for k in range(0, int(worksheet.cell_value(i, 1))):
                        codes[iter].prize = worksheet.cell_value(i, 0)
                        iter += 1
        session.commit()
        bot.send_message(message.chat.id, 'Схоже що дані були успішно додані до базі даних!')
    except Exception as e:
        print('Exeption from add_promo_items')
        bot.send_message(message.chat.id, e)
        session.rollback()
    finally:
        print('Finaly block')
        os.remove(file_path)
        handle_admin(message)
